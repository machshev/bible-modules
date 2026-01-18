"""Parse Nouns."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebNoun",
    "is_noun",
)

# TODO: this needs to move to a separate file
COMMON_NOUNS = (
    "יִשְׂרָאֵל",
    "מֶלֶךְ",
    "אֶרֶץ",
    "בֶּן",
    "בַיִת",
    "עַם",
    "אִישׁ",
    "יוֹם",
    "דִּבֶּר",
    "פְּנֵי",
    "אֱלֹהִים",
    "שָׁם",
    "דּוֹד",
    "מִצְרִים",
    "עִיר",
    "אֲדֹנָי",
    "אָדָם",
    "יַד",
    "יְרוּשָׁלִַם",
    "שָׁנָה",
    "כֹהֵן",
    "שָׁאוּל",
    "מָיִם",
    "דֶּרֶךְ",
    "גוֹיִם",
    "אִשָּׁה",
    "שָׁמַיִם",
    "הַר",
    "זָהָב",
    "אוֹת",
    "קֹדֶשׁ",
    "חֶרֶב",
    "רֹב",
    "אֵשׁ",
    "יַעֲקֹב",
    "קוֹל",
    "יְהוּדָה",
    "מֹשֶׁה",
    "אֶחָד",
    "טוֹב",
    "עוֹלָם",
    "עֶשְׂרִים",
    "אֶלֶף",
    "מִזְבֵּחַ",
    "מָקוֹם",
    "רוּחַ",
    "רָע",
    "רֹאשׁ",
    "פַרְעֹה",
    "שַׁעַר",
    "שָׂדֶה",
)
COMMON_NOUNS_CONST = tuple(constanants(w) for w in COMMON_NOUNS)


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
    if constanants(elements.word) not in COMMON_NOUNS_CONST:
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
