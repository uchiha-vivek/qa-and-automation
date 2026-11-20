"""Example API tests. Use them as a style guide, then add your own files (test_tickets.py, ...)."""
import pytest


@pytest.mark.smoke
def test_health_returns_ok(api):
    response = api.get(f"{api.base}/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.smoke
def test_create_ticket_returns_ai_fields(make_ticket):
    ticket = make_ticket()
    for field in ("id", "category", "priority", "sentiment", "confidence", "suggested_reply"):
        assert field in ticket, f"missing field: {field}"
    assert ticket["status"] == "open"


# TODO: add your tests. Ideas: validation (parametrize!), filters, search, override, audit log,
#       metrics, 404s, rate limit (429), response schema, PII in suggested_reply, ...
