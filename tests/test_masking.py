"""Tests for masking Swedish personal identity numbers (methodology E4 SKA 3).

Only Skatteverket's well-known test number (19)121212-1212 and variants of it are used —
never numbers from real books.
"""

import pytest

from accounting_agent.books import contains_personal_number, mask_personal_numbers

MASK = "[personal number]"


@pytest.mark.parametrize(
    "number",
    [
        "121212-1212",  # 10 digits with separator
        "121212+1212",  # '+' separator (100 years or older)
        "19121212-1212",  # 12 digits with separator
        "191212121212",  # 12 digits, no separator
    ],
)
def test_personal_numbers_are_masked(number: str) -> None:
    text = f"Swish from parent {number} for training"

    assert mask_personal_numbers(text) == f"Swish from parent {MASK} for training"
    assert contains_personal_number(text)


def test_several_numbers_in_one_text_are_all_masked() -> None:
    text = "121212-1212 and 191212121212"

    assert mask_personal_numbers(text) == f"{MASK} and {MASK}"


@pytest.mark.parametrize(
    "text",
    [
        "2026-09-25",  # ISO date
        "-1305.55",  # amount
        "1930",  # account number
        "0066_2026-03-05.md",  # voucher file name
        "Ref (3011114295631)",  # 13-digit bank reference
        "Invoice 52086",  # invoice number
    ],
)
def test_ordinary_numbers_are_left_alone(text: str) -> None:
    assert mask_personal_numbers(text) == text
    assert not contains_personal_number(text)


def test_text_without_digits_is_unchanged() -> None:
    assert mask_personal_numbers("Hyra för mars") == "Hyra för mars"
