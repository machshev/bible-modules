"""Parse Nouns."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebNoun",
    "is_noun",
)


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    raw: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel


def is_noun(elements: CommonElements) -> HebNoun | None:
    """Is the word a Noun?"""
    if True:
        return None

    gender = ""
    number = ""

    return HebNoun(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        gender=gender,
        number=number,
        word_constanants=constanants(elements.word),
        word=elements.word,
        raw=elements.raw,
    )
