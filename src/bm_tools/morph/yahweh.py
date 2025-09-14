"""Parse the memorial name."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "Yahweh",
    "is_yahweh",
)


@dataclass(frozen=True)
class Yahweh:
    """The name."""

    word: str
    word_constanants: str
    raw: str
    preposition: str | None
    vav_consec: bool = False


def is_yahweh(elements: CommonElements) -> Yahweh | None:
    """Is the word Yahweh?"""
    word_constanants = constanants(elements.word)

    if word_constanants == "יהוה":
        return Yahweh(
            preposition=elements.preposition,
            word_constanants=constanants(elements.raw),
            word=elements.raw,
            raw=elements.raw,
        )

    return None
