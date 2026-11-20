"""Runtime configuration for TriageBot. Values can be overridden with environment variables."""
import os

APP_VERSION = "1.0.0"

# "mock" (default, no API key needed) or "claude" (needs ANTHROPIC_API_KEY)
LLM_MODE = os.getenv("LLM_MODE", "mock").lower()
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")

DB_PATH = os.getenv("TRIAGEBOT_DB", "triagebot.db")

MAX_MESSAGE_LENGTH = 5000
MAX_SUBJECT_LENGTH = 200
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

CATEGORIES = ["billing", "technical", "account", "shipping", "general"]
PRIORITIES = ["P1", "P2", "P3", "P4"]
SENTIMENTS = ["positive", "neutral", "negative", "angry"]
