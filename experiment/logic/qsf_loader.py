from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlparse


QSF_PATH = Path(__file__).resolve().parent.parent.parent / "source" / "qualtrics_export.qsf"


@lru_cache(maxsize=1)
def load_qsf() -> dict:
    data = json.loads(QSF_PATH.read_text(encoding="utf-8"))
    questions = {
        element["PrimaryAttribute"]: element["Payload"]
        for element in data["SurveyElements"]
        if element["Element"] == "SQ"
    }
    options = next(
        element["Payload"]
        for element in data["SurveyElements"]
        if element["Element"] == "SO"
    )
    return {
        "survey_name": data["SurveyEntry"]["SurveyName"],
        "questions": questions,
        "options": options,
    }


def get_question(question_id: str) -> dict:
    return load_qsf()["questions"][question_id]


def question_html(question_id: str) -> str:
    return get_question(question_id).get("QuestionText", "")


def export_tag(question_id: str) -> str:
    return get_question(question_id).get("DataExportTag", question_id)


def question_choices(question_id: str) -> list[dict[str, str]]:
    question = get_question(question_id)
    choices = question.get("Choices", {})
    order = question.get("ChoiceOrder", [])
    recodes = question.get("RecodeValues", {})
    ordered_choices = []
    for choice_id in order:
        key = str(choice_id)
        if key not in choices:
            continue
        ordered_choices.append(
            {
                "id": key,
                "value": recodes.get(key, key),
                "display": choices[key]["Display"],
            }
        )
    return ordered_choices


def prolific_completion_url() -> str:
    return load_qsf()["options"].get("EOSRedirectURL", "")


def prolific_completion_code() -> str:
    completion_url = prolific_completion_url()
    if not completion_url:
        return ""
    query = parse_qs(urlparse(completion_url).query)
    return query.get("cc", [""])[0]
