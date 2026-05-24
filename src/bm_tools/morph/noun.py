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

# Suffix tables: each maps suffix-string → (gender, number).
# Empty string means "unknown from suffix alone — derive from the lemma form."
# Tried longest-first so that יהם is not partially matched as הם.
_THREE_CHAR_SUFFIXES: dict[str, tuple[str, str]] = {
    "יכם": ("", "p"),
    "יכן": ("", "p"),
    "יהם": ("", "p"),
    "יהן": ("", "p"),
    "ינו": ("", "p"),
}

_TWO_CHAR_SUFFIXES: dict[str, tuple[str, str]] = {
    "כם": ("", "p"),  # 2mp pronominal
    "כן": ("", "p"),  # 2fp pronominal
    "נו": ("", "p"),  # 1cp pronominal
    "הם": ("", "p"),  # 3mp pronominal
    "הן": ("", "p"),  # 3fp pronominal
    "ים": ("m", "p"),  # masculine plural ending
    "ות": ("f", "p"),  # feminine plural ending
    "הו": ("", "s"),  # 3ms pronominal
    "יו": ("", "s"),  # 3ms pronominal (his)
    "יה": ("", "s"),  # 3fs pronominal (her)
    "יך": ("", "s"),  # 2ms/2fs pronominal
    "ין": ("", "p"),  # Aramaic plural
}

_ONE_CHAR_SUFFIXES: dict[str, tuple[str, str]] = {
    "ך": ("", "s"),  # 2ms/2fs pronominal
    "ו": ("", "s"),  # 3ms pronominal
    "א": ("", "s"),  # Aramaic emphatic state
    "י": ("", "s"),  # 1cs pronominal
    "ה": ("f", "s"),  # FS noun ending or 3fs pronominal
    "ם": ("", "p"),  # 3mp pronominal (alternate)
    "ן": ("", "p"),  # 3fp pronominal (alternate)
    "ת": ("f", "s"),  # FS construct ending
}


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    vav_consec: bool
    raw: str
    gender: str  # i.e. (m)asculine, (f)eminine
    number: str  # i.e. (s)ingular, (p)lural, (d)ual


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
    # Absolute ה dropped in construct/suffixed form
    if stem + "ה" in _BDB_NOUN_LEMMAS:
        return stem + "ה"
    return None


def _gender_number_from_lemma(lemma: str) -> tuple[str, str]:
    """Infer gender and number from the lemma's consonant form."""
    if lemma.endswith("ים"):
        return ("m", "p")
    if lemma.endswith("ות"):
        return ("f", "p")
    if lemma.endswith("ה"):
        return ("f", "s")
    return ("m", "s")


def _match_suffix(cons: str) -> tuple[str, str, str, str] | None:
    """Try suffix candidates longest-first.

    Returns (lemma, gender, number, matched_suffix) or None.
    """
    candidates: list[tuple[str, str, str]] = []

    if len(cons) > 3:  # noqa: PLR2004
        sfx3 = cons[-3:]
        if sfx3 in _THREE_CHAR_SUFFIXES:
            g, n = _THREE_CHAR_SUFFIXES[sfx3]
            candidates.append((cons[:-3], g, n))

    if len(cons) > 2:  # noqa: PLR2004
        sfx2 = cons[-2:]
        if sfx2 in _TWO_CHAR_SUFFIXES:
            g, n = _TWO_CHAR_SUFFIXES[sfx2]
            candidates.append((cons[:-2], g, n))

    if len(cons) > 1:
        sfx1 = cons[-1]
        if sfx1 in _ONE_CHAR_SUFFIXES:
            g, n = _ONE_CHAR_SUFFIXES[sfx1]
            candidates.append((cons[:-1], g, n))

    for stem, g, n in candidates:
        found_lemma = _lookup_stem(stem)
        if found_lemma:
            return found_lemma, g, n, cons[len(stem) :]

    return None


def is_noun(elements: CommonElements) -> HebNoun | None:
    """Is the word a Noun?"""
    cons = constanants(elements.word)

    if cons in _BDB_NOUN_LEMMAS:
        gender, number = _gender_number_from_lemma(cons)
        found_lemma = cons
    else:
        result = _match_suffix(cons)
        if result is None:
            return None
        found_lemma, gender, number, matched_suffix = result

        # ת suffix is FP when the lemma is masculine (no ה ending), and FS
        # construct when the absolute form ends in ה.
        tav_fs = matched_suffix == "ת" and gender == "f" and number == "s"
        if tav_fs and not found_lemma.endswith("ה"):
            number = "p"

        # For pronominal suffixes the suffix alone doesn't tell us the noun's
        # own gender/number — fall back to the lemma form.
        if not gender or not number:
            lg, ln = _gender_number_from_lemma(found_lemma)
            gender = gender or lg
            number = number or ln

    return HebNoun(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        vav_consec=elements.vav_consec,
        gender=gender,
        number=number,
        word_constanants=found_lemma,
        word=elements.word,
        raw=elements.raw,
    )
