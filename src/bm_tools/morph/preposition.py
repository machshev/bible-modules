"""Preposition parser."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

HEBREW_PREPOSITIONS = (
    "אָשֵׁר",  # That
    "אֲשֶׁר",  # That
    "אַשֶׁר",  # That
    "אַשֻּׁר",  # That
    "כִּי",  # For
    "עַל",  # Upon
    "אֶל",  # To
    "לֹא",  # No/Not
    "אַל",  # No/Not
    "כָּל",  # All
    "עַד",  # Until
    "אִם",  # With
    "כָל",  # All
)

__all__ = (
    "HebPreposition",
    "is_preposition",
)


@dataclass(frozen=True)
class HebPreposition:
    """Hebrew Preposition."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None


def is_preposition(elements: CommonElements) -> HebPreposition | None:
    """Is the word a preposition."""
    if elements.word not in HEBREW_PREPOSITIONS:
        return None

    return HebPreposition(
        preposition=elements.preposition,
        vav_consec=elements.vav_consec,
        definite_article=elements.definite_article,
        word=elements.word,
        word_constanants=constanants(elements.word),
        raw=elements.raw,
    )
