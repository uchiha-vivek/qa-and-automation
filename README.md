# TriageBot — QA / SDET Assignment

TriageBot is a small **AI-powered customer-support triage app**. A customer submits a complaint;
an AI model classifies it (category, priority, sentiment), detects the language and drafts a reply.
Support agents can override the AI's decision.

**Your job: you are the QA engineer for this product.** The app works, but it has not been tested.
Over 10 days you will test it manually, evaluate the AI, automate tests, and handle a product update.

- **Start with [`ASSIGNMENT.md`](ASSIGNMENT.md)** — it has the day-by-day tasks.
- Expected behaviour is defined in [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md).

---

## 1. Setup (about 10 minutes)

**You need:** Python 3.10+, Git, a code editor (VS Code recommended), and a browser.

```bash
# 1. Fork this repo on GitHub (button at the top right), then clone YOUR fork
git clone https://github.com/<your-username>/qa-and-automation.git
cd qa-and-automation

# 2. Create a virtual environment and install everything
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r submissions/automation/requirements-test.txt
playwright install chromium

# 3. (Optional) load 15 sample tickets
python -m app.seed

# 4. Start the app
uvicorn app.main:app --reload --port 8000
```

Open:
- **Web app:** http://localhost:8000
- **API docs (Swagger):** http://localhost:8000/docs ← you can call every API from here
- **Health check:** http://localhost:8000/api/health

On Mac/Linux, `make install`, `make run`, `make seed`, `make reset` and `make test` do the same things.

**Start from a clean database:** stop the app, delete `triagebot.db`, then start it again.

## 2. How the AI works

```
Ticket ──► app/triage.py ──► builds prompt (app/prompts/triage_prompt.txt + data/knowledge_base/)
                         ──► LLM provider (mock or real Claude) ──► JSON ──► saved to SQLite
```

- **Mock mode (default):** `app/llm/mock_llm.py` behaves like a real LLM (including some of its
  typical failure modes) but runs offline, for free. **No API key is needed for this assignment.**
- **Real mode (optional, bonus):** `pip install anthropic`, then
  `LLM_MODE=claude ANTHROPIC_API_KEY=... uvicorn app.main:app --port 8000`.
- Settings are in `app/config.py` and can be overridden with environment variables (see `.env.example`).

## 3. Project layout

```
app/                      the product (FastAPI backend + HTML/JS UI)
  llm/                    LLM providers (mock + real)
  prompts/                the system prompt sent to the model
data/knowledge_base/      company policies the AI must follow
data/sample_tickets.csv   sample data
docs/PRODUCT_SPEC.md      requirements = source of truth
templates/                templates for your deliverables
submissions/              YOUR WORK GOES HERE
  manual/                 test plan, test cases, bug reports
  ai_eval/                golden dataset + AI evaluation report
  automation/             pytest API tests, Playwright UI tests, AI eval tests
.github/workflows/ci.yml  CI pipeline (you complete it)
```

## 4. Ground rules
- **Do not fix bugs in `app/`.** You are QA: find them, report them, and write tests that catch them.
  (Exception: a bonus task may ask you to.)
- Commit **at least once a day** with clear messages. We review your commit history.
- Write all deliverables in `submissions/`. Markdown or CSV is fine; no Word or Excel needed.
- You may use any AI assistant, but you must understand and be able to explain everything you submit.
