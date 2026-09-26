"""Masking of Swedish personal identity numbers (personnummer) in output.

The pattern is the one the organisations' own tooling already relies on: 6–8 digits, a
``-`` or ``+`` separator and up to 4 digits; or 12 digits that start with a plausible
century, month and day. Longer digit runs (bank references) are not matched.
"""

import re

MASK = "[personal number]"
PERSONAL_NUMBER = re.compile(
    r"(?<!\d)\d{6,8}[-+]\d{1,4}(?!\d)"
    r"|(?<!\d)(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{4}(?!\d)"
)


def contains_personal_number(text: str) -> bool:
    """True if ``text`` appears to contain a personal identity number."""
    return PERSONAL_NUMBER.search(text) is not None


def mask_personal_numbers(text: str) -> str:
    """Replace every personal identity number in ``text`` with ``[personal number]``."""
    return PERSONAL_NUMBER.sub(MASK, text)
