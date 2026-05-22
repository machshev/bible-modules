"""Parse Nouns."""

from dataclasses import dataclass
from pathlib import Path

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebNoun",
    "is_noun",
)

_DATA_FILE = Path(__file__).parent / "data" / "bdb_noun_lemmas.txt"
_BDB_NOUN_LEMMAS: frozenset[str] = frozenset(
    _DATA_FILE.read_text(encoding="utf-8").splitlines()
)


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    vav_consec: bool
    raw: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel


def is_noun(elements: CommonElements) -> HebNoun | None:
    """Is the word a Noun?"""
    if constanants(elements.word) not in _BDB_NOUN_LEMMAS:
        return None

    gender = ""
    number = ""

    return HebNoun(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        vav_consec=elements.vav_consec,
        gender=gender,
        number=number,
        word_constanants=constanants(elements.word),
        word=elements.word,
        raw=elements.raw,
    )
