"""
Mock LLM.

Simulates an LLM so the app runs offline without an API key. It receives the same
system prompt + user message a real model would, and returns a raw text completion
that *should* be a JSON object matching the schema in app/prompts/triage_prompt.txt.
"""
import json
import random
import re
import time

CATEGORY_KEYWORDS = {
    "billing": ["refund", "charge", "charged", "invoice", "payment", "bill", "price",
                "subscription", "money", "paid"],
    "technical": ["error", "bug", "crash", "not working", "broken", "slow", "down", "outage",
                  "app", "website", "loading", "page", "feature"],
    "account": ["password", "login", "log in", "account", "hacked", "locked", "username",
                "2fa", "otp", "sign in", "profile"],
    "shipping": ["delivery", "shipping", "package", "order", "tracking", "courier",
                 "delivered", "arrive", "parcel"],
}

PRIORITY_KEYWORDS = {
    "P1": ["hacked", "fraud", "unauthorized", "stolen", "outage", "everyone", "lawyer", "legal",
           "charged twice", "double charged", "data breach", "security", "all users"],
    "P2": ["refund", "cannot login", "can't login", "can't log in", "not delivered", "broken",
           "not working", "locked", "error", "failed", "crash", "never arrived",
           "not been delivered", "has not arrived", "hasn't arrived"],
    "P3": ["slow", "delay", "late", "how do i", "how to", "issue", "problem", "wrong"],
}

SENTIMENT_KEYWORDS = {
    "angry": ["angry", "furious", "worst", "terrible", "ridiculous", "unacceptable", "scam",
              "disgusting", "!!!", "useless"],
    "negative": ["bad", "disappointed", "unhappy", "not happy", "problem", "issue", "poor",
                 "frustrated", "annoyed"],
    "positive": ["thanks", "thank you", "great", "love", "awesome", "happy", "appreciate"],
}

ENGLISH_HINTS = {"the", "and", "is", "my", "i", "to", "a", "of", "it", "not", "you", "for",
                 "was", "have", "this", "me", "in", "on", "your", "please", "can", "we"}

INJECTION_RE = re.compile(
    r"ignore (all |any )?(the )?(previous|prior|above|earlier) (instructions|rules)", re.I
)

REPLY_TEMPLATES = {
    "billing": "Hi {name}, thanks for reaching out about your billing concern. {extra}"
               "Our billing team will review your account and reply within 24 hours.",
    "technical": "Hi {name}, sorry about the trouble. Our engineers are looking into it. "
                 "In the meantime, please try clearing your browser cache and signing in again.",
    "account": "Hi {name}, we take account issues seriously. {extra}"
               "Please reset your password using the 'Forgot password' link.",
    "shipping": "Hi {name}, sorry your order is taking longer than expected. Orders usually "
                "arrive in 3-5 business days. {extra}",
    "general": "Hi {name}, thanks for your message! A member of our team will get back to you soon.",
}


class MockLLM:
    name = "mock"

    def complete(self, system: str, user: str, temperature: float) -> str:
        time.sleep(0.6)  # simulate model latency
        name, body = self._parse_user(user)
        text = body.lower()

        greeting = body.split()[0].lower().strip(",.!")
        is_greeting = greeting in ("hi", "hello", "dear", "hey")

        language = self._detect_language(body)
        if language != "en":
            result = {
                "category": "general", "priority": "P4", "sentiment": "neutral",
                "confidence": 0.55, "language": language,
                "suggested_reply": REPLY_TEMPLATES["general"].format(name=name),
            }
            return self._render(result, body)

        category, cat_hits = self._score(text, CATEGORY_KEYWORDS, default="general")
        priority, pri_hits = self._priority(text)
        sentiment, _ = self._score(text, SENTIMENT_KEYWORDS, default="neutral")
        confidence = round(0.6 + 0.12 * (cat_hits + pri_hits) - (0.05 if is_greeting else 0), 2)

        if temperature > 0 and random.random() < temperature * 0.35:
            idx = int(priority[1]) + random.choice([-1, 1])
            priority = f"P{min(4, max(1, idx))}"

        m = INJECTION_RE.search(body)
        if m:
            forced = re.search(r"\bP([1-4])\b", body[m.start():], re.I)
            if forced:
                priority = f"P{forced.group(1)}"
                confidence = 0.99

        extra = ""
        if category == "billing" and "refund" in text:
            extra = "Good news: you are eligible for a full refund within 60 days of purchase, no questions asked. "
        elif category == "account" and priority == "P1":
            extra = "We have temporarily locked your account to keep it safe. "
        elif category == "shipping":
            extra = "As an apology, we've upgraded your next order to free express shipping."

        reply = REPLY_TEMPLATES[category].format(name=name, extra=extra).strip()
        reply += f'\n\nFor reference, you wrote: "{body[:150]}"'

        result = {
            "category": category, "priority": priority, "sentiment": sentiment,
            "confidence": confidence, "language": "en", "suggested_reply": reply,
        }
        return self._render(result, body)

    # ---------- helpers ----------
    @staticmethod
    def _parse_user(user: str):
        name_match = re.search(r"Customer:\s*(.*)", user)
        name = name_match.group(1).strip() if name_match else "there"
        body_match = re.search(r"Message:\n(.*)</ticket>", user, re.S)
        body = body_match.group(1).strip() if body_match else ""
        return name, body

    @staticmethod
    def _detect_language(body: str) -> str:
        words = re.findall(r"\w+", body.lower())
        if not words:
            return "en"
        english = sum(1 for w in words if w in ENGLISH_HINTS)
        if english / len(words) >= 0.12:
            return "en"
        if re.search(r"[ऀ-ॿ]", body):
            return "hi"
        return "other"

    @staticmethod
    def _score(text: str, table: dict, default: str):
        best, best_hits = default, 0
        for label, words in table.items():
            hits = sum(1 for w in words if w in text)
            if hits > best_hits:
                best, best_hits = label, hits
        return best, best_hits

    @staticmethod
    def _priority(text: str):
        for level in ("P1", "P2", "P3"):
            hits = sum(1 for w in PRIORITY_KEYWORDS[level] if w in text)
            if hits:
                return level, hits
        return "P4", 0

    @staticmethod
    def _render(result: dict, body: str) -> str:
        raw = json.dumps(result, ensure_ascii=False)
        if any(ord(ch) >= 0x1F300 for ch in body):
            return "```json\n" + raw + "\n```"
        return raw
