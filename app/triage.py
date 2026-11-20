"""Triage pipeline: build prompt -> call LLM -> parse -> post-process."""
import json
import re
from pathlib import Path

from app import config
from app.llm import get_provider

ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = ROOT / "app" / "prompts" / "triage_prompt.txt"
KB_DIR = ROOT / "data" / "knowledge_base"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
CARD_RE = re.compile(r"\b\d{16}\b")


def load_knowledge_base() -> str:
    parts = [f"## {p.stem}\n{p.read_text()}" for p in sorted(KB_DIR.glob("*.md"))]
    return "\n\n".join(parts)


def build_system_prompt() -> str:
    return PROMPT_FILE.read_text().replace("{knowledge_base}", load_knowledge_base())


def build_user_message(customer_name: str, subject: str, message: str) -> str:
    return (
        "<ticket>\n"
        f"Customer: {customer_name}\n"
        f"Subject: {subject}\n"
        f"Message:\n{message}\n"
        "</ticket>"
    )


def mask_pii(text: str) -> str:
    text = EMAIL_RE.sub("[email]", text)
    text = CARD_RE.sub("[card]", text)
    return text


def triage_ticket(customer_name: str, subject: str, message: str) -> dict:
    provider = get_provider()
    raw = provider.complete(
        system=build_system_prompt(),
        user=build_user_message(customer_name, subject, message),
        temperature=config.LLM_TEMPERATURE,
    )
    data = json.loads(raw)
    data["suggested_reply"] = mask_pii(data.get("suggested_reply", ""))
    data.setdefault("language", "en")
    return data
