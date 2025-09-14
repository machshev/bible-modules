"""Parse the article."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebArticle",
    "is_article",
)


@dataclass(frozen=True)
class HebArticle:
    """Hebrew Definite Article."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool = False
    definite_article: bool = True
    preposition: str | None = None


def is_article(elements: CommonElements) -> HebArticle | None:
    """Is the word the definite article."""
    word_constanants = constanants(elements.word)

    if word_constanants == "את":
        return HebArticle(
            preposition=elements.preposition,
            vav_consec=elements.vav_consec,
            definite_article=elements.definite_article,
            word=elements.word,
            word_constanants=word_constanants,
            raw=elements.raw,
        )

    return None
