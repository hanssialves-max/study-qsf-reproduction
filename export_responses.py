from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


METADATA_FIELDS = [
    "timestamp_utc",
    "event",
    "prolific_pid",
    "study_id",
    "session_id",
]


def load_completed_rows(source: Path) -> list[dict[str, str]]:
    rows = []
    if not source.exists():
        return rows

    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event") != "study_complete":
                continue
            row = {field: event.get(field, "") for field in METADATA_FIELDS}
            row.update(event.get("responses", {}))
            rows.append(row)
    return rows


def write_wide_csv(rows: list[dict[str, str]], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    response_fields = sorted(
        {
            field
            for row in rows
            for field in row
            if field not in METADATA_FIELDS
        }
    )
    fieldnames = METADATA_FIELDS + response_fields
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export completed study responses to a wide CSV file.")
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        help="Directory containing response_events.jsonl.",
    )
    parser.add_argument(
        "--output",
        default="data/exports/responses_wide.csv",
        help="CSV file to create.",
    )
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    output = Path(args.output)
    rows = load_completed_rows(raw_dir / "response_events.jsonl")
    write_wide_csv(rows, output)
    print(f"Exported {len(rows)} completed response(s) to {output}")


if __name__ == "__main__":
    main()
