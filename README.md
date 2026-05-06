# Qualtrics QSF Reproduction

This project reproduces the Qualtrics study exported in [source/qualtrics_export.qsf](/C:/Users/alveshbv/Documents/Codex%20Test/study-qsf-reproduction/source/qualtrics_export.qsf).

## What it reproduces

- mobile-device screen-out
- consent page that requires typing `yes`
- Prolific ID and residency pre-screen
- demographics block
- instruction page
- eight diversity-rating items
- ethnicity question
- comment plus honeypot question
- debrief page with Prolific completion handling

The wording and answer options are loaded from the QSF export, so the Python version stays close to the original Qualtrics study.

## Quick start

1. Create a virtual environment:
   `python -m venv .venv`
2. Install dependencies:
   `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
3. Run the app:
   `.\.venv\Scripts\python.exe run.py`
4. Open:
   `http://127.0.0.1:5000/?PROLIFIC_PID=test_pid&STUDY_ID=test_study&SESSION_ID=test_session`

## Data output

Local pilot data is written to:

- `data/raw/participants.csv`
- `data/raw/response_events.jsonl`

## Render

The included `render.yaml` is set up for a free Render deployment. If you want to override the Prolific completion settings, set:

- `SECRET_KEY`
- `COMPLETION_CODE`
- `PROLIFIC_RETURN_URL`

## RUB Server Deployment

This app can also run on the central SOCO server via Docker Compose.

Expected server path:

`/srv/soco-studies/apps/study-qsf-reproduction`

Expected public path:

`https://soco.vm.ruhr-uni-bochum.de/qsf-demo`

Server data path:

`/srv/soco-studies/data/qsf-demo`
