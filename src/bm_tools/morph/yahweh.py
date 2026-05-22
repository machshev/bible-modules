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


_INSEP_PREP_CONS = ("ב", "כ", "ל", "מ", "ה")


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

    # Handle preposition + Yahweh where the preposition was not stripped
    # (e.g. לַיהוָה, בַּיהוָה) because the vowel pattern is non-standard
    if word_constanants.endswith("יהוה") and len(word_constanants) > 4:  # noqa: PLR2004
        prefix = word_constanants[:-4]
        if len(prefix) == 1 and prefix in _INSEP_PREP_CONS:
            return Yahweh(
                preposition=prefix,
                word_constanants=word_constanants,
                word=elements.word,
                raw=elements.raw,
            )

    return None
