"""Parse Adverbs."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebAdverb",
    "is_adverb",
)

HEB_ADVERB = (
    # Participle
    "גַּם",  # Also, even
    "אַף",  # Also/even
    "אַךְ",  # Surly
    "רַק",  # Only
    "הִנֵּה",  # Behold
    "נָא",  # Please now
    "כֹּה",  # So
    "עַד",  # Until
    "עוֹד",  # further
    "כֵן",  # Yes / it is so
    "אַחֲרֵי",  # After
)


@dataclass(frozen=True)
class HebAdverb:
    """Hebrew Adverb."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    vav_consec: bool
    raw: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel


def is_adverb(elements: CommonElements) -> HebAdverb | None:
    """Is the word a Adverb?"""
    if elements.word not in HEB_ADVERB:
        return None

    gender = ""
    number = ""

    return HebAdverb(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        vav_consec=elements.vav_consec,
        gender=gender,
        number=number,
        word_constanants=constanants(elements.word),
        word=elements.word,
        raw=elements.raw,
    )
