"""Parse Nouns."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants, load_bdb_noun_lemmas
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebNoun",
    "is_noun",
)

_BDB_NOUN_LEMMAS: frozenset[str] = load_bdb_noun_lemmas()

# Map regular consonant forms to final forms (for BDB lookup after suffix stripping)
_REGULAR_TO_FINAL = {"מ": "ם", "נ": "ן", "כ": "ך", "פ": "ף", "צ": "ץ"}


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


def _lookup_stem(stem: str) -> str | None:
    """Look up stem in BDB, trying final-form conversion and ה-restoration."""
    if stem in _BDB_NOUN_LEMMAS:
        return stem
    # BDB uses final-form consonants at word end
    final_stem = stem[:-1] + _REGULAR_TO_FINAL.get(stem[-1], stem[-1]) if stem else stem
    if final_stem in _BDB_NOUN_LEMMAS:
        return final_stem
    # Construct ת → absolute ה (e.g. תשוקת → תשוקה, נשמת → נשמה)
    if stem and stem[-1] == "ת":
        he_stem = stem[:-1] + "ה"
        if he_stem in _BDB_NOUN_LEMMAS:
            return he_stem
    # Absolute ה dropped in construct/suffixed form (e.g. זע → זעה, פי → not needed)
    if stem + "ה" in _BDB_NOUN_LEMMAS:
        return stem + "ה"
    return None


def is_noun(elements: CommonElements) -> HebNoun | None:
    """Is the word a Noun?"""
    cons = constanants(elements.word)
    if cons not in _BDB_NOUN_LEMMAS:
        # Build candidate stems by trying 2-char then 1-char suffix stripping.
        # Both are tried independently so that e.g. פניך strips ך (not יך) → פני.
        # Single-consonant: ך (2ms/2fs), ו (3ms suffix)  # noqa: RUF003
        # Multi-consonant: כם (2mp), כן (2fp), נו (1cp), הם (3mp), הן (3fp)
        # Aramaic emphatic state: א suffix
        candidates: list[str] = []
        # 3-char suffixes on construct-plural nouns: יכם (2mp), יכן (2fp), יהם (3mp), יהן (3fp), ינו (1cp)
        if len(cons) > 3 and cons[-3:] in ("יכם", "יכן", "יהם", "יהן", "ינו"):  # noqa: PLR2004
            candidates.append(cons[:-3])
        if len(cons) > 2 and cons[-2:] in ("כם", "כן", "נו", "הם", "הן", "ים", "ות", "הו", "יו", "יה", "יך", "ין"):  # noqa: PLR2004
            candidates.append(cons[:-2])
        if len(cons) > 1 and cons[-1] in ("ך", "ו", "א", "י", "ה", "ם", "ן", "ת"):
            candidates.append(cons[:-1])

        found = None
        for stem in candidates:
            found = _lookup_stem(stem)
            if found:
                break

        if found is None:
            return None
        cons = found

    gender = ""
    number = ""

    return HebNoun(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        vav_consec=elements.vav_consec,
        gender=gender,
        number=number,
        word_constanants=cons,
        word=elements.word,
        raw=elements.raw,
    )
