"""Morphology helpers."""

from bm_tools.morph.constants import (
    HEBREW_VOWELS,
)


def is_consanant(char: str) -> bool:
    """Is the character a consanant."""
    return "א" <= char <= "ת"


def is_vowel(char: str) -> bool:
    """Is the character a vowel."""
    return char in HEBREW_VOWELS


def constanants(text: str) -> str:
    """Return a string containing only hebrew consanants."""
    return "".join([char for char in text if is_consanant(char)])


def normalise(text: str) -> str:
    """Return a string containing only hebrew consanants and vowels."""
    return "".join([char for char in text if is_consanant(char) or is_vowel(char)])
