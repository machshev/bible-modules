"""Hebrew word utility functions."""

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from logzero import logger

__all__ = (
    "is_consanant",
    "is_vowel",
    "morph_eval",
    "normalise",
    "parse_bible",
)

# ruff: noqa: RUF001
HEBREW_CONSANANTS = (
    "א",
    "ב",
    "ג",
    "ד",
    "ה",
    "ו",
    "ז",
    "ח",
    "ט",
    "י",
    "כ",
    "ך",  # Final Kaf
    "ל",
    "מ",
    "ם",  # Final Mem
    "נ",
    "ן",  # Final Nun
    "ס",
    "ע",
    "פ",
    "ף",  # Final Pe
    "צ",
    "ץ",  # Final Tzadi
    "ק",
    "ר",
    "שׁ",
    "ת",
)

HEBREW_GUTERALS_WEAK = (
    "א",
    "ע",
    "ר",
)

HEBREW_GUTERALS_HARSH = (
    "ה",
    "ח",
)

HEBREW_GUTERALS = HEBREW_GUTERALS_HARSH + HEBREW_GUTERALS_WEAK

HEBREW_INSEPARABLE_PREPOSITIONS = (
    "ב",
    "כ",
    "ל",
    "מ",
    # "ש",
)


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

HEB_SHEVA = chr(0x05B0)
HEB_HATAF_SEGOL = chr(0x05B1)
HEB_HATAF_PATAH = chr(0x05B2)
HEB_HATAF_QAMATS = chr(0x05B3)

HEB_HIRIQ = chr(0x05B4)
HEB_TSERE = chr(0x05B5)
HEB_SEGOL = chr(0x05B6)
HEB_PATAH = chr(0x05B7)
HEB_QAMATS = chr(0x05B8)
HEB_QAMATS_QATAN = chr(0x05C7)
HEB_QUBUTS = chr(0x05BB)

HEB_HOLAM = chr(0x05B9)
HEB_HOLAM_HASER = chr(0x05BA)  # for Vav

HEB_DAGESH = chr(0x05BC)
HEB_MAPIQ = chr(0x05BC)

HEB_SHIN_DOT = chr(0x05C1)
HEB_SIN_DOT = chr(0x05C2)

HEBREW_VOWELS = (
    HEB_SHEVA,
    HEB_HATAF_SEGOL,
    HEB_HATAF_PATAH,
    HEB_HATAF_QAMATS,
    HEB_HIRIQ,
    HEB_TSERE,
    HEB_SEGOL,
    HEB_PATAH,
    HEB_QAMATS,
    HEB_QAMATS_QATAN,
    HEB_QUBUTS,
    HEB_HOLAM,
    HEB_HOLAM_HASER,
    HEB_DAGESH,
    HEB_MAPIQ,
    HEB_SHIN_DOT,
    HEB_SIN_DOT,
)

HEB_SUFFIX = (
    HEB_PATAH + "ה",  # perf.s.3.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_QAMATS,  # perf.s.2.m
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA,  # perf.s.2.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_HIRIQ + "י",  # perf.s.2.f
    "ו" + HEB_DAGESH,  # perf.pl.3.c
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA + "ם",  # perf.s.2.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA + "ן",  # perf.s.2.f
    HEB_SHEVA + "נו" + HEB_DAGESH,  # perf.pl.1.c
    # Nouns
    HEB_HIRIQ + "י",  # to me
    "ו" + HEB_HOLAM,  # to him
    "ך" + HEB_QAMATS_QATAN,  # to you (s.2.m)
    HEB_PATAH + "י",  # my
    HEB_QAMATS + "י",  # my
    HEB_QAMATS_QATAN + "י",  # my
    HEB_TSERE + "י",  # of
    HEB_QAMATS + "ה",  # Her
    HEB_HIRIQ + "ים",  # Pl.m
    "ו" + HEB_HOLAM + "ת",  # Pl.f
    HEB_SEGOL + "ת",  # Pl.f
    HEB_HIRIQ + "ית",  # Pl.f
)

HEB_PREFIX = (
    "י" + HEB_SHEVA,  # y'
    "י" + HEB_HIRIQ,  # Yi
    "י" + HEB_PATAH,  # Ya
    "י" + HEB_QAMATS,  # Ya
    "י" + HEB_QAMATS_QATAN,  # Ya
    "י" + HEB_DAGESH + HEB_SHEVA,  # y'
    "י" + HEB_DAGESH + HEB_HIRIQ,  # Yi
    "י" + HEB_DAGESH + HEB_PATAH,  # Ya
    "ת" + HEB_HIRIQ,  # Ti
    "א" + HEB_SEGOL,  # 'e
)


@dataclass(frozen=True)
class Yahweh:
    """The name."""

    word: str
    word_constanants: str
    raw: str
    preposition: str | None
    vav_consec: bool = False


@dataclass(frozen=True)
class HebUnknown:
    """Unknown Hebrew word."""

    word: str
    raw: str
    word_constanants: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel
    prefix: str = ""
    suffix: str = ""
    vav_consec: bool = False
    definite_article: bool = False
    preposition: str | None = None


@dataclass(frozen=True)
class HebArticle:
    """Hebrew Definite Article."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool = False
    definite_article: bool = True
    preposition: str | None = None


@dataclass(frozen=True)
class HebPreposition:
    """Hebrew Preposition."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None


@dataclass(frozen=True)
class HebVerb:
    """Hebrew Verb."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel
    tense: str | None
    mood: str | None


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


ParsedWord = Yahweh | HebArticle | HebPreposition | HebNoun | HebVerb | HebUnknown


def is_consanant(char: str) -> bool:
    """Is the character a consanant."""
    return "א" <= char <= "ת"


def is_vowel(char: str) -> bool:
    """Is the character a vowel."""
    return char in HEBREW_VOWELS


def constanants(text: str) -> str:
    """Return a string containing only hebrew consanants."""
    return "".join([char for char in text if is_consanant(char)])


def normalise(text: str) -> str:
    """Return a string containing only hebrew consanants and vowels."""
    return "".join([char for char in text if is_consanant(char) or is_vowel(char)])


def parse_vav_consecutive(raw: str) -> tuple[str, bool]:
    """Parse vav consecutive."""
    if raw[0] == "ו" and raw[1] in (
        HEB_SHEVA,
        HEB_PATAH,
    ):
        return raw[2:], True

    return raw, False


def parse_definite_article(raw: str) -> tuple[str, bool]:
    """Parse the definite article."""
    if len(raw) < 4 or raw[0] != "ה":  # noqa: PLR2004
        return raw, False

    if raw[2] in HEBREW_GUTERALS:
        if any(
            [
                # Segol following Chet Qamats
                (
                    raw[1] == HEB_SEGOL
                    and raw[2] in ("ה", "ע", "ח")
                    and raw[3] == HEB_QAMATS
                ),
                # Qamats following accented Hey or Ayin Qamats
                raw[1] == HEB_QAMATS and raw[2] in ("ה", "ע") and raw[3] == HEB_QAMATS,
                # Weak guteral
                raw[2] in HEBREW_GUTERALS_WEAK and raw[1] == HEB_QAMATS,
                # Strong guteral
                raw[2] in HEBREW_GUTERALS_HARSH and raw[1] == HEB_PATAH,
            ]
        ):
            return raw[2:], True

        return raw, False

    # Normal so expect dargesh
    # Skip shin/sin dot
    i = 4 if raw[3] in (HEB_SHIN_DOT, HEB_SIN_DOT) else 3

    if raw[1] == HEB_PATAH and raw[i] == HEB_DAGESH:
        return raw[2:i] + raw[i + 1 :], True

    return raw, False


def parse_inseparable_prepositions(raw: str) -> tuple[str, str | None, bool]:
    """Parse inseparable prepositions."""
    if len(raw) < 5 or raw[0] not in HEBREW_INSEPARABLE_PREPOSITIONS:  # noqa: PLR2004
        return (raw, None, False)

    word = raw
    preposition = None
    definite_article = False

    i = 2 if raw[1] == HEB_DAGESH else 1

    if (raw[0] in ("ב", "כ") and raw[1] == HEB_DAGESH) or (raw[0] == "ל"):
        # TODO: Special cases Yahweh and Elohim

        if any(
            [
                # Standard preposition
                raw[i] == HEB_SHEVA,
                # Before Sheva, point with hiriq
                (raw[i] == HEB_HIRIQ and raw[i + 2] == HEB_SHEVA),
                # Before Composite/hataf Sheva, point with the corresponding short vowel
                (raw[i] == HEB_PATAH and raw[i + 2] == HEB_HATAF_PATAH),
                (raw[i] == HEB_SEGOL and raw[i + 2] == HEB_HATAF_SEGOL),
                (raw[i] == HEB_QAMATS and raw[i + 2] == HEB_HATAF_QAMATS),
            ]
        ):
            preposition = raw[0]
            word = raw[i + 1 :]

        # Before Yod Sheva
        elif raw[i] == HEB_HIRIQ and raw[i + 1] == "י":
            preposition = raw[0]
            word = "י" + HEB_SHEVA + raw[i + 2 :]

        # Check for the article
        elif raw[i] in (HEB_PATAH, HEB_SEGOL, HEB_QAMATS):
            word, definite_article = parse_definite_article(raw="ה" + raw[i:])
            if definite_article:
                preposition = raw[0]

    elif raw[0] == "מ":
        # Definite article is preserved in full after preposition `Min` and
        # since the article is ה which is guteral, we only check the article
        # here in this path.
        if raw[1] == HEB_TSERE and raw[2] in HEBREW_GUTERALS:
            preposition = raw[0]
            word, definite_article = parse_definite_article(raw=raw[2:])

        elif raw[1] == HEB_HIRIQ and raw[3] == HEB_DAGESH:
            preposition = raw[0]
            word = raw[2] + raw[4:]

    return (word, preposition, definite_article)


def explode(raw: str) -> tuple[str, str, str]:
    """Separate a word into it's grammatical parts."""
    prefix = ""
    suffix = ""

    for s in HEB_PREFIX:
        if raw.startswith(s):
            prefix = s
            break

    for s in HEB_SUFFIX:
        if raw.endswith(s):
            suffix = s
            break

    # remove prefix/sufix
    word = raw[len(prefix) : len(raw) - len(suffix)]

    return word, prefix, suffix


def grammar(raw: str) -> tuple[str, str, str, str, str]:
    """Grammatical evaluation."""
    word = raw
    gender = ""
    number = ""
    tense = ""
    mood = ""

    return word, gender, number, tense, mood


def morph_eval(raw: str) -> ParsedWord:
    """Evaluate the Morphology of a word."""
    if len(raw) <= 1:
        # Single letters, not sure what to do with these?
        # Is this an error?
        return HebUnknown(
            word=raw,
            word_constanants=constanants(raw),
            raw=raw,
        )

    word, vav_cons = parse_vav_consecutive(raw=raw)
    word, full_definite_article = parse_definite_article(raw=word)
    word, preposition, definite_article = parse_inseparable_prepositions(raw=word)
    word_constanants = constanants(word)

    # Yahweh
    if word_constanants == "יהוה":
        return Yahweh(
            preposition=preposition,
            word_constanants=constanants(raw),
            word=raw,
            raw=raw,
        )

    # Definite Article
    if word_constanants == "את":
        return HebArticle(
            preposition=preposition,
            vav_consec=vav_cons,
            definite_article=definite_article,
            word=word,
            word_constanants=word_constanants,
            raw=raw,
        )

    word, prefix, suffix = explode(raw=word)
    word, gender, number, tense, mood = grammar(raw=word)

    word_constanants = constanants(word)

    # Known prepositions
    if word in HEBREW_PREPOSITIONS:
        return HebPreposition(
            preposition=preposition,
            vav_consec=vav_cons,
            definite_article=definite_article,
            word=word,
            word_constanants=word_constanants,
            raw=raw,
        )

    if False:  # preposition or definite_article:
        # Add this back in when we can differentiate between verbs and nouns
        return HebVerb(
            preposition=preposition,
            definite_article=definite_article,
            number=number,
            tense=tense,
            mood=mood,
            word=word_constanants,
            raw=raw,
        )

    return HebUnknown(
        word=word,
        word_constanants=word_constanants,
        raw=raw,
        gender=gender,
        number=number,
        vav_consec=vav_cons,
        definite_article=full_definite_article or definite_article,
        preposition=preposition,
        prefix=prefix,
        suffix=suffix,
    )


def parse_bible(
    db: sqlite3.Connection,
) -> tuple[Mapping[str, ParsedWord], Mapping[str, int]]:
    """Parse the bible and evaluate each word's morphology.

    Args:
        db: connection to an SQLite3 haqor db.

    Returns:
        tuple containing mapping of parsed words, and a mapping of word
        occorance count.
    """
    parsed_words = {}
    count = {}

    for result in db.execute("SELECT words FROM hebrew WHERE book <= 39"):
        for raw in result[0].split(" "):
            normalised = normalise(text=raw)

            if not normalised:
                continue

            # Already evaluated just increment the count
            if normalised in parsed_words:
                word = parsed_words[normalised]

            else:
                # New word seen so work out the morphology and add to the cache
                word = morph_eval(raw=normalised)
                parsed_words[normalised] = word

            count[word.word_constanants] = count.get(word.word_constanants, 0) + 1

    db.execute(
        """CREATE TABLE words(
            raw TEXT,
            word TEXT,
            constanants TEXT,
            count INT,
            unknown BOOL,
            vav_con BOOL,
            article BOOL,
            prepositions TEXT,
            gender TEXT,
            number TEXT,
            prefix TEXT,
            suffix TEXT
        )"""
    )

    for raw, word in parsed_words.items():
        if isinstance(word, HebUnknown):
            db.execute(
                "INSERT INTO words VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    raw,
                    word.word,
                    word.word_constanants,
                    count[word.word_constanants],
                    True,
                    word.vav_consec,
                    word.definite_article,
                    word.preposition,
                    word.gender,
                    word.number,
                    word.prefix,
                    word.suffix,
                ),
            )
            continue

        db.execute(
            "INSERT INTO words VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                raw,
                word.word,
                word.word_constanants,
                count[word.word_constanants],
                False,
                word.vav_consec,
                False,
                word.preposition,
                "",
                "",
                "",
                "",
            ),
        )

    db.commit()

    return parsed_words, count


def review(
    *,
    index: int = 0,
    rows: int | None = None,
    unknowns: bool = False,
) -> None:
    """Review the morphology results."""
    db_path = Path.cwd() / "modules" / "haqor" / "haqor.db"

    db = sqlite3.connect(db_path)

    for idx, result in enumerate(
        db.execute("SELECT raw FROM words ORDER BY count DESC")
    ):
        if idx < index:
            continue

        morph = morph_eval(raw=result[0])

        if unknowns and not isinstance(morph, HebUnknown):
            continue

        logger.info("[%i] %s: %s", idx, morph.raw[::-1], morph)

        if rows is not None:
            rows -= 1
            if not rows:
                break
