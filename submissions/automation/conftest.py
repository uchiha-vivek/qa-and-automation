"""Shared fixtures. `base_url` comes from pytest.ini (override with --base-url)."""
import uuid

import pytest
import requests


@pytest.fixture(scope="session")
def api(base_url):
    """A requests.Session with the base URL handy: api.post(f"{api.base}/api/tickets", ...)."""
    session = requests.Session()
    session.base = base_url
    return session


@pytest.fixture
def make_ticket(api):
    """Factory fixture: creates a ticket through the API and returns the response JSON."""

    def _make(**overrides):
        payload = {
            "customer_name": "QA Bot",
            "email": f"qa+{uuid.uuid4().hex[:6]}@example.com",
            "subject": "Automated test ticket",
            "message": "The website shows an error when I open my orders page.",
            **overrides,
        }
        response = api.post(f"{api.base}/api/tickets", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
