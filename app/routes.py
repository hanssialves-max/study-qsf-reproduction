from experiment.logic.storage import append_response_event, append_session_row, utc_now_iso
from experiment.surveys.qsf_study import (
    CONSENT,
    DDEMOS,
    DEBRIEF,
    DIVERSITY_ITEMS,
    ETHNICITY,
    HONEY,
    INSTRUCTION,
    MOBILE_ERROR_HTML,
    PRE_SCREEN,
    STUDY_TITLE,
)
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

bp = Blueprint("main", __name__)


def capture_prolific_params() -> None:
    for query_key, session_key in (
        ("PROLIFIC_PID", "prolific_pid"),
        ("STUDY_ID", "study_id"),
        ("SESSION_ID", "session_id"),
    ):
        value = request.args.get(query_key)
        if value:
            session[session_key] = value


def session_payload() -> dict[str, str]:
    return {
        "prolific_pid": session.get("prolific_pid", ""),
        "study_id": session.get("study_id", ""),
        "session_id": session.get("session_id", ""),
    }


def response_payload() -> dict[str, str]:
    return session.setdefault("qsf_responses", {})


def save_response(key: str, value: str) -> None:
    payload = response_payload()
    payload[key] = value
    session["qsf_responses"] = payload


def is_mobile_device() -> bool:
    user_agent = request.headers.get("User-Agent", "").lower()
    mobile_markers = ["iphone", "android", "mobile", "ipad"]
    return any(marker in user_agent for marker in mobile_markers)


@bp.route("/")
def index():
    capture_prolific_params()
    if is_mobile_device():
        return render_template(
            "screenout.html",
            study_title=STUDY_TITLE,
            message_html=MOBILE_ERROR_HTML,
        )
    return redirect(url_for("main.consent"))


@bp.route("/consent", methods=["GET", "POST"])
def consent():
    capture_prolific_params()
    if is_mobile_device():
        return render_template(
            "screenout.html",
            study_title=STUDY_TITLE,
            message_html=MOBILE_ERROR_HTML,
        )
    if request.method == "POST":
        consent_value = request.form.get(CONSENT["field_name"], "").strip()
        session["consent_given"] = consent_value == "yes"
        save_response(CONSENT["field_name"], consent_value)
        if session["consent_given"]:
            return redirect(url_for("main.pre_screen"))
        return render_template(
            "consent.html",
            participant=session_payload(),
            study_title=STUDY_TITLE,
            consent=CONSENT,
            error="Please type the word yes to continue.",
        )
    return render_template(
        "consent.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        consent=CONSENT,
    )


@bp.route("/pre-screen", methods=["GET", "POST"])
def pre_screen():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))

    if request.method == "POST":
        prolific_id = request.form.get(PRE_SCREEN["prolific"]["field_name"], "").strip()
        residency = request.form.get(PRE_SCREEN["residency"]["field_name"], "")
        save_response(PRE_SCREEN["prolific"]["field_name"], prolific_id)
        save_response(PRE_SCREEN["residency"]["field_name"], residency)
        if prolific_id:
            session["prolific_pid"] = prolific_id
        if residency != "1":
            return render_template(
                "screenout.html",
                study_title=STUDY_TITLE,
                message_html=PRE_SCREEN["mismatch_html"],
            )
        return redirect(url_for("main.demos"))

    return render_template(
        "pre_screen.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        pre_screen=PRE_SCREEN,
    )


@bp.route("/demos", methods=["GET", "POST"])
def demos():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))

    if request.method == "POST":
        age = request.form.get(DDEMOS["age"]["field_name"], "").strip()
        gender = request.form.get(DDEMOS["gender"]["field_name"], "")
        save_response(DDEMOS["age"]["field_name"], age)
        save_response(DDEMOS["gender"]["field_name"], gender)
        if not gender:
            return render_template(
                "demos.html",
                participant=session_payload(),
                study_title=STUDY_TITLE,
                demos=DDEMOS,
                error="Please answer the required question before continuing.",
            )
        return redirect(url_for("main.instructions"))

    return render_template(
        "demos.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        demos=DDEMOS,
    )


@bp.route("/instructions", methods=["GET", "POST"])
def instructions():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))
    if request.method == "POST":
        return redirect(url_for("main.diversity"))
    return render_template(
        "display_page.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        body_html=INSTRUCTION["html"],
        button_label="Continue",
    )


@bp.route("/diversity", methods=["GET", "POST"])
def diversity():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))

    if request.method == "POST":
        responses = {}
        missing = False
        for item in DIVERSITY_ITEMS:
            value = request.form.get(item["field_name"], "")
            responses[item["field_name"]] = value
            save_response(item["field_name"], value)
            if not value:
                missing = True
        if missing:
            return render_template(
                "diversity.html",
                participant=session_payload(),
                study_title=STUDY_TITLE,
                items=DIVERSITY_ITEMS,
                error="Please answer all items before continuing.",
            )
        append_response_event(
            current_app.config["RAW_DATA_DIR"],
            {
                "event": "diversity_block_submit",
                **session_payload(),
                "consent_given": bool(session.get("consent_given")),
                "responses": responses,
            },
        )
        return redirect(url_for("main.ethnicity"))

    return render_template(
        "diversity.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        items=DIVERSITY_ITEMS,
    )


@bp.route("/ethnicity", methods=["GET", "POST"])
def ethnicity():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))

    if request.method == "POST":
        ethnicity_value = request.form.get(ETHNICITY["field_name"], "")
        save_response(ETHNICITY["field_name"], ethnicity_value)
        if not ethnicity_value:
            return render_template(
                "single_choice.html",
                participant=session_payload(),
                study_title=STUDY_TITLE,
                item=ETHNICITY,
                error="Please answer the required question before continuing.",
            )
        return redirect(url_for("main.honey"))

    return render_template(
        "single_choice.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        item=ETHNICITY,
    )


@bp.route("/honey", methods=["GET", "POST"])
def honey():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))

    if request.method == "POST":
        comment = request.form.get(HONEY["comment"]["field_name"], "").strip()
        honeypot = request.form.get(HONEY["honeypot"]["field_name"], "")
        save_response(HONEY["comment"]["field_name"], comment)
        save_response(HONEY["honeypot"]["field_name"], honeypot)
        if not honeypot:
            return render_template(
                "honey.html",
                participant=session_payload(),
                study_title=STUDY_TITLE,
                honey=HONEY,
                error="Please answer the required question before continuing.",
            )
        return redirect(url_for("main.complete"))

    return render_template(
        "honey.html",
        participant=session_payload(),
        study_title=STUDY_TITLE,
        honey=HONEY,
    )


@bp.route("/complete")
def complete():
    if not session.get("consent_given"):
        return redirect(url_for("main.consent"))

    if not session.get("completion_logged"):
        metadata = {
            "timestamp_utc": utc_now_iso(),
            "event": "study_complete",
            **session_payload(),
            "consent_given": bool(session.get("consent_given")),
            "response_count": len(response_payload()),
        }
        append_session_row(current_app.config["RAW_DATA_DIR"], metadata)
        append_response_event(
            current_app.config["RAW_DATA_DIR"],
            {
                "event": "study_complete",
                **session_payload(),
                "responses": response_payload(),
            },
        )
        session["completion_logged"] = True

    completion_code = current_app.config["COMPLETION_CODE"] or DEBRIEF["completion_code"]
    prolific_return_url = current_app.config["PROLIFIC_RETURN_URL"] or DEBRIEF["completion_url"]
    complete_url = prolific_return_url or url_for("main.index", _external=True)
    return render_template(
        "complete.html",
        body_html=DEBRIEF["html"],
        completion_code=completion_code,
        complete_url=complete_url,
        participant=session_payload(),
        prolific_return_url=prolific_return_url,
        study_title=STUDY_TITLE,
    )
