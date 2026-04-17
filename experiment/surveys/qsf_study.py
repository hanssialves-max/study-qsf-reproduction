from experiment.logic.qsf_loader import (
    export_tag,
    prolific_completion_code,
    prolific_completion_url,
    question_choices,
    question_html,
)


STUDY_TITLE = "What drives (perceived) diversity? - Experiment U.S. Ethnicities 8 Distributions"

QUESTION_IDS = {
    "mobile_error": "QID31",
    "consent": "QID32",
    "prolific_id": "QID33",
    "residency": "QID37",
    "residency_mismatch": "QID38",
    "intro": "QID7",
    "age": "QID8",
    "gender": "QID9",
    "instruction": "QID42",
    "diversity": ["QID12", "QID48", "QID46", "QID49", "QID45", "QID50", "QID47", "QID51"],
    "ethnicity": "QID52",
    "comment": "QID14",
    "honeypot": "QID15",
    "debrief": "QID41",
}


CONSENT = {
    "qid": QUESTION_IDS["consent"],
    "html": question_html(QUESTION_IDS["consent"]),
    "field_name": export_tag(QUESTION_IDS["consent"]),
}

PRE_SCREEN = {
    "prolific": {
        "qid": QUESTION_IDS["prolific_id"],
        "html": question_html(QUESTION_IDS["prolific_id"]),
        "field_name": export_tag(QUESTION_IDS["prolific_id"]),
    },
    "residency": {
        "qid": QUESTION_IDS["residency"],
        "html": question_html(QUESTION_IDS["residency"]),
        "field_name": export_tag(QUESTION_IDS["residency"]),
        "choices": question_choices(QUESTION_IDS["residency"]),
    },
    "mismatch_html": question_html(QUESTION_IDS["residency_mismatch"]),
}

DDEMOS = {
    "intro_html": question_html(QUESTION_IDS["intro"]),
    "age": {
        "qid": QUESTION_IDS["age"],
        "html": question_html(QUESTION_IDS["age"]),
        "field_name": export_tag(QUESTION_IDS["age"]),
    },
    "gender": {
        "qid": QUESTION_IDS["gender"],
        "html": question_html(QUESTION_IDS["gender"]),
        "field_name": export_tag(QUESTION_IDS["gender"]),
        "choices": question_choices(QUESTION_IDS["gender"]),
    },
}

INSTRUCTION = {
    "qid": QUESTION_IDS["instruction"],
    "html": question_html(QUESTION_IDS["instruction"]),
}

DIVERSITY_ITEMS = [
    {
        "qid": qid,
        "field_name": export_tag(qid),
        "html": question_html(qid),
        "choices": question_choices(qid),
    }
    for qid in QUESTION_IDS["diversity"]
]

ETHNICITY = {
    "qid": QUESTION_IDS["ethnicity"],
    "html": question_html(QUESTION_IDS["ethnicity"]),
    "field_name": export_tag(QUESTION_IDS["ethnicity"]),
    "choices": question_choices(QUESTION_IDS["ethnicity"]),
}

HONEY = {
    "comment": {
        "qid": QUESTION_IDS["comment"],
        "html": question_html(QUESTION_IDS["comment"]),
        "field_name": export_tag(QUESTION_IDS["comment"]),
    },
    "honeypot": {
        "qid": QUESTION_IDS["honeypot"],
        "html": question_html(QUESTION_IDS["honeypot"]),
        "field_name": export_tag(QUESTION_IDS["honeypot"]),
        "choices": question_choices(QUESTION_IDS["honeypot"]),
    },
}

DEBRIEF = {
    "qid": QUESTION_IDS["debrief"],
    "html": question_html(QUESTION_IDS["debrief"]),
    "completion_code": prolific_completion_code(),
    "completion_url": prolific_completion_url(),
}

MOBILE_ERROR_HTML = question_html(QUESTION_IDS["mobile_error"])
