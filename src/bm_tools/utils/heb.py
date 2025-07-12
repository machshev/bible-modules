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

HEBREW_INSEPARABLE_PREPOSITIONS = (
    "ב",
    "ה",
    "ו",
    "כ",
    "ל",
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
)

HEB_PREFIX = (
    "י" + HEB_SHEVA,  # y'
    "י" + HEB_HIRIQ,  # Yi
    "י" + HEB_PATAH,  # Ya
    "י" + HEB_DAGESH + HEB_SHEVA,  # y'
    "י" + HEB_DAGESH + HEB_HIRIQ,  # Yi
    "י" + HEB_DAGESH + HEB_PATAH,  # Ya
    "ת" + HEB_HIRIQ,  # Ti
    "א" + HEB_SEGOL,  # 'e
)


@dataclass(frozen=True)
class Yahweh:
    """The name."""

    preposition: str | None
    word: str
    raw: str


@dataclass(frozen=True)
class HebUnknown:
    """Unknown Hebrew word."""

    word: str
    raw: str
    preposition: str | None = None
    definite_article: bool = False
    prefix: str = ""
    suffix: str = ""


@dataclass(frozen=True)
class HebArticle:
    """Hebrew Definite Article."""

    preposition: str | None
    definite_article: bool
    word: str
    raw: str


@dataclass(frozen=True)
class HebPreposition:
    """Hebrew Preposition."""

    preposition: str | None
    definite_article: bool
    word: str
    raw: str


@dataclass(frozen=True)
class HebVerb:
    """Hebrew Verb."""

    preposition: str | None
    definite_article: bool
    number: int | None
    tense: str | None
    mood: str | None
    word: str
    raw: str


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    raw: str


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


def inseparable_prepositions(raw: str) -> tuple[str, str | None, bool]:
    """Parse inseparable prepositions."""
    word = raw
    preposition = None
    definite_article = False
    if raw[0] in HEBREW_INSEPARABLE_PREPOSITIONS and raw[1] in (
        HEB_SHEVA,
        HEB_PATAH,
        HEB_QAMATS,
        HEB_QAMATS_QATAN,
    ):
        if raw[1] in (HEB_PATAH, HEB_QAMATS, HEB_QAMATS_QATAN):
            definite_article = True

        preposition = raw[0]
        word = raw[2:]

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


def grammar(raw: str) -> tuple[str, int | None, str | None, str | None]:
    """Grammatical evaluation."""
    word = raw
    number = None
    tense = None
    mood = None

    # remove prefix/sufix

    return word, number, tense, mood


def morph_eval(raw: str) -> ParsedWord:
    """Evaluate the Morphology of a word."""
    if len(raw) <= 1:
        # Single letters, not sure what to do with these?
        # Is this an error?
        return HebUnknown(word=raw, raw=raw)

    word, preposition, definite_article = inseparable_prepositions(raw=raw)
    word_constanants = constanants(word)

    # Yahweh
    if word_constanants == "יהוה":
        return Yahweh(
            preposition=preposition,
            word=constanants(raw),
            raw=raw,
        )

    # Definite Article
    if word_constanants == "את":
        return HebArticle(
            preposition=preposition,
            definite_article=definite_article,
            word=word_constanants,
            raw=raw,
        )

    word, prefix, suffix = explode(raw=word)
    word, number, tense, mood = grammar(raw=word)

    word_constanants = constanants(word)

    # Known prepositions
    if word in HEBREW_PREPOSITIONS:
        return HebPreposition(
            preposition=preposition,
            definite_article=definite_article,
            word=word_constanants,
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
        word=word_constanants,
        raw=raw,
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

            count[word.word] = count.get(word.word, 0) + 1

    db.execute(
        """CREATE TABLE words(
            raw TEXT,
            word TEXT,
            count INT,
            unknown BOOL,
            prefix TEXT,
            suffix TEXT
        )"""
    )

    for raw, word in parsed_words.items():
        if isinstance(word, HebUnknown):
            db.execute(
                "INSERT INTO words VALUES (?,?,?,?,?,?)",
                (
                    raw,
                    word.word,
                    count[word.word],
                    True,
                    word.prefix,
                    word.suffix,
                ),
            )
            continue

        db.execute(
            "INSERT INTO words VALUES (?,?,?,?,?,?)",
            (
                raw,
                word.word,
                count[word.word],
                False,
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
