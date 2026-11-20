from app import config


def get_provider():
    """Return the configured LLM provider."""
    if config.LLM_MODE == "claude":
        from app.llm.claude_llm import ClaudeLLM
        return ClaudeLLM()
    from app.llm.mock_llm import MockLLM
    return MockLLM()
