"""Load data/sample_tickets.csv into the database.  Usage:  python -m app.seed"""
import csv
from pathlib import Path

from app import db
from app.triage import triage_ticket

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_tickets.csv"


def main() -> None:
    db.init_db()
    with SAMPLE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        result = triage_ticket(row["customer_name"], row["subject"], row["message"])
        db.insert_ticket({**row, **result})
        print(f"  seeded: {row['subject'][:50]!r:55} -> {result['priority']} / {result['category']}")
    print(f"Seeded {len(rows)} tickets.")


if __name__ == "__main__":
    main()
