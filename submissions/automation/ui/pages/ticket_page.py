"""Page Object for the TriageBot main page."""
from playwright.sync_api import Page, expect


class TicketPage:
    def __init__(self, page: Page):
        self.page = page
        self.name = page.get_by_test_id("input-name")
        self.email = page.get_by_test_id("input-email")
        self.subject = page.get_by_test_id("input-subject")
        self.message = page.get_by_test_id("input-message")
        self.submit_btn = page.get_by_test_id("submit-btn")
        self.form_status = page.get_by_test_id("form-status")
        self.rows = page.get_by_test_id("ticket-row")
        self.detail = page.get_by_test_id("ticket-detail")

    def open(self):
        self.page.goto("/")
        expect(self.page.get_by_test_id("app-version")).not_to_be_empty()
        return self

    def submit_ticket(self, name, email, subject, message):
        self.name.fill(name)
        self.email.fill(email)
        self.subject.fill(subject)
        self.message.fill(message)
        self.submit_btn.click()

    # TODO: add methods such as filter_by_priority(), search(), open_ticket(), override(...)
