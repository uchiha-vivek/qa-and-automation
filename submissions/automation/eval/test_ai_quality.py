"""
AI quality gates (Day 9). These tests should FAIL the build when AI quality is not good enough.
Remove the skip marker when you start working on a test.
"""
import pytest

CATEGORY_TARGET = 0.85
PRIORITY_TARGET = 0.80


@pytest.mark.ai
@pytest.mark.skip(reason="TODO Day 9")
def test_golden_set_category_accuracy():
    ...


@pytest.mark.ai
@pytest.mark.skip(reason="TODO Day 9")
def test_golden_set_priority_accuracy():
    ...


@pytest.mark.ai
@pytest.mark.skip(reason="TODO Day 9")
def test_prompt_injection_does_not_change_priority():
    ...


@pytest.mark.ai
@pytest.mark.skip(reason="TODO Day 9")
def test_reply_never_contains_pii():
    ...


@pytest.mark.ai
@pytest.mark.skip(reason="TODO Day 9")
def test_same_input_same_output():
    ...
