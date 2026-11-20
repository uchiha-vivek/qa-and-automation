import re

from playwright.sync_api import expect

from ui.pages.ticket_page import TicketPage


def test_submit_ticket_shows_ai_result(page):
    tickets = TicketPage(page).open()
    tickets.submit_ticket(
        name="UI Tester",
        email="ui@example.com",
        subject="Cannot login",
        message="I cannot login to my account, it says my password is wrong.",
    )
    expect(tickets.form_status).to_have_text(re.compile(r"Created ticket #\d+"), timeout=10_000)
    expect(tickets.detail).to_be_visible()


# TODO: add your UI tests (filters, search, details, override, XSS (UI-04), double submit (UI-05) ...)
