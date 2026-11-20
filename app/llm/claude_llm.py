"""Real LLM provider (optional). Requires: pip install anthropic, and ANTHROPIC_API_KEY set."""
import os

from app import config


class ClaudeLLM:
    name = "claude"

    def __init__(self):
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError("LLM_MODE=claude but ANTHROPIC_API_KEY is not set")
        import anthropic  # imported lazily so mock mode needs no extra packages
        self.client = anthropic.Anthropic()

    def complete(self, system: str, user: str, temperature: float) -> str:
        response = self.client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=800,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text
