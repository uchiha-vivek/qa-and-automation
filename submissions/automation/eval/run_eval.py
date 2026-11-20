"""
Runs the golden dataset against the API and prints accuracy.

Usage (app must be running):
    python submissions/automation/eval/run_eval.py submissions/ai_eval/golden_set.csv
"""
import csv
import sys

import requests

BASE_URL = "http://localhost:8000"


def run(golden_path: str) -> list:
    results = []
    with open(golden_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            response = requests.post(f"{BASE_URL}/api/tickets", json={
                "customer_name": "Eval Runner",
                "email": "eval@example.com",
                "subject": "",
                "message": row["message"],
            })
            if response.status_code != 201:
                print(f"{row['id']}: HTTP {response.status_code}")
                results.append({**row, "predicted_category": "ERROR", "predicted_priority": "ERROR"})
                continue
            ticket = response.json()
            results.append({**row, "predicted_category": ticket["category"],
                            "predicted_priority": ticket["priority"]})
    return results


def summarize(results: list) -> None:
    # TODO: print category accuracy, priority accuracy, and a priority confusion matrix.
    #       Bonus: accuracy per language; write results to a CSV for your report.
    for r in results:
        print(r["id"], r["expected_priority"], "->", r["predicted_priority"])


if __name__ == "__main__":
    summarize(run(sys.argv[1] if len(sys.argv) > 1 else "submissions/ai_eval/golden_set.csv"))
