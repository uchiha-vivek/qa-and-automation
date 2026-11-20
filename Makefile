.PHONY: install run seed reset test

install:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r submissions/automation/requirements-test.txt

run:
	.venv/bin/uvicorn app.main:app --reload --port 8000

seed:
	.venv/bin/python -m app.seed

reset:
	rm -f triagebot.db && echo "Database deleted. Restart the app to recreate it."

test:
	.venv/bin/pytest submissions/automation
