import csv
import json
import shutil
from pathlib import Path
from uuid import uuid4

from app import create_app


def make_local_tmp_dir() -> Path:
    target = Path(__file__).resolve().parent / "_tmp" / uuid4().hex
    target.mkdir(parents=True, exist_ok=True)
    return target


def test_app_creation():
    app = create_app()
    assert app is not None


def test_core_routes_and_prolific_capture():
    tmp_path = make_local_tmp_dir()
    try:
        app = create_app()
        app.config["TESTING"] = True
        app.config["RAW_DATA_DIR"] = tmp_path
        client = app.test_client()

        response = client.get("/?PROLIFIC_PID=p1&STUDY_ID=s1&SESSION_ID=ss1")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/consent")

        consent_get = client.get("/consent")
        assert consent_get.status_code == 200
        assert b"type the word yes" in consent_get.data

        guarded = client.get("/diversity", follow_redirects=False)
        assert guarded.status_code == 302

        consent_post = client.post("/consent", data={"IC": "yes"}, follow_redirects=False)
        assert consent_post.status_code == 302
        assert consent_post.headers["Location"].endswith("/pre-screen")

        pre_screen = client.post(
            "/pre-screen",
            data={"PID": "p1", "Residency": "1"},
            follow_redirects=False,
        )
        assert pre_screen.status_code == 302
        assert pre_screen.headers["Location"].endswith("/demos")
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_completion_writes_flat_files():
    tmp_path = make_local_tmp_dir()
    try:
        app = create_app()
        app.config["TESTING"] = True
        app.config["RAW_DATA_DIR"] = tmp_path
        client = app.test_client()

        client.get("/?PROLIFIC_PID=p2&STUDY_ID=s2&SESSION_ID=ss2")
        client.post("/consent", data={"IC": "yes"})
        client.post("/pre-screen", data={"PID": "p2", "Residency": "1"})
        client.post("/demos", data={"Age": "30", "Gender": "2"})
        client.post("/instructions")
        client.post(
            "/diversity",
            data={
                "Div_S_White-dom": "1",
                "Div_S_Black-dom": "2",
                "Div_S_White-abs": "3",
                "Div_S_Black-abs": "4",
                "Div_B_White-dom": "5",
                "Div_B_Black-dom": "6",
                "Div_B_White-abs": "7",
                "Div_B_Black-abs": "1",
            },
        )
        client.post("/ethnicity", data={"Ethnicity": "3"})
        completion = client.post(
            "/honey",
            data={
                "Comment": "Interesting study",
                "Honeypot": "4",
            },
            follow_redirects=True,
        )

        assert completion.status_code == 200
        assert b"Completion Code" in completion.data

        csv_file = tmp_path / "participants.csv"
        jsonl_file = tmp_path / "response_events.jsonl"
        assert csv_file.exists()
        assert jsonl_file.exists()

        with csv_file.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 1
        assert rows[0]["prolific_pid"] == "p2"
        assert rows[0]["response_count"] == "16"

        with jsonl_file.open("r", encoding="utf-8") as handle:
            first = json.loads(handle.readline())
            second = json.loads(handle.readline())
        assert first["prolific_pid"] == "p2"
        assert first["responses"]["Div_B_Black-dom"] == "6"
        assert second["responses"]["Honeypot"] == "4"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_non_us_residency_shows_screenout():
    tmp_path = make_local_tmp_dir()
    try:
        app = create_app()
        app.config["TESTING"] = True
        app.config["RAW_DATA_DIR"] = tmp_path
        client = app.test_client()

        client.post("/consent", data={"IC": "yes"})
        response = client.post(
            "/pre-screen",
            data={"PID": "p3", "Residency": "2"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"cannot continue with this study" in response.data
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
