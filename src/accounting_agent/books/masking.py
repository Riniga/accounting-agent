"""Masking of Swedish personal identity numbers (personnummer) in output.

Two shapes are recognised:

- with a separator or a century, as the organisations' own tooling already relied on:
  6–8 digits, a ``-`` or ``+`` separator and up to 4 digits; or 12 digits that start with
  a plausible century, month and day;
- ten digits in a row (MVP-005), as a bank's text can hold them. Ten digits are also
  phone numbers, references and organisation numbers, so these count only with a real
  month and day and a correct check digit.

Longer digit runs (bank references) are not matched.
"""

import re

MASK = "[personal number]"
# Files the core writes are Swedish and use the organisations' own mask text (ADR-008).
FILE_MASK = "[personnummer]"
PERSONAL_NUMBER = re.compile(
    r"(?<!\d)\d{6,8}[-+]\d{1,4}(?!\d)"
    r"|(?<!\d)(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{4}(?!\d)"
)
# YYMMDD and four digits. The day may be 61–91: a coordination number adds 60 to it.
TEN_DIGITS = re.compile(
    r"(?<!\d)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]|6[1-9]|[78]\d|9[01])\d{4}(?!\d)"
)


def contains_personal_number(text: str) -> bool:
    """True if ``text`` appears to contain a personal identity number."""
    return PERSONAL_NUMBER.search(text) is not None or any(
        _has_check_digit(match.group()) for match in TEN_DIGITS.finditer(text)
    )


def mask_personal_numbers(text: str, mask: str = MASK) -> str:
    """Replace every personal identity number in ``text`` with ``mask``."""
    masked = PERSONAL_NUMBER.sub(mask, text)
    return TEN_DIGITS.sub(
        lambda match: mask if _has_check_digit(match.group()) else match.group(),
        masked,
    )


def _has_check_digit(number: str) -> bool:
    """True if the last of the ten digits is the Luhn check digit of the other nine.

    About one in ten other numbers passes by chance; a reference masked by mistake is
    a smaller harm than a personal identity number left in the books.
    """
    total = 0
    for position, character in enumerate(number):
        product = int(character) * (2 if position % 2 == 0 else 1)
        # A two-digit product counts as the sum of its digits.
        total += product - 9 if product > 9 else product
    return total % 10 == 0
