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
    "ל",
    "מ",
    "נ",
    "ס",
    "ע",
    "פ",
    "צ",
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
    "אֶת",  # Definite article
    "אֵת",  # Definite article
    "אֲשֶׁר",  # That
    "כִּי",  # For
    "עַל",  # Upon
    "אֶל",  # To
    "לֹא",  # No/Not
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


@dataclass(frozen=True)
class HebUnknown:
    """Unknown Hebrew word."""

    word: str
    raw: str


@dataclass(frozen=True)
class HebPreposition:
    """Hebrew Preposition."""

    word: str
    raw: str


@dataclass(frozen=True)
class HebVerb:
    """Hebrew Verb."""

    preposition: str | None
    definite_article: bool
    word: str
    raw: str


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    raw: str


ParsedWord = HebPreposition | HebNoun | HebVerb | HebUnknown


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


def morph_eval(raw: str) -> ParsedWord:
    """Evaluate the Morphology of a word."""
    word = raw

    if len(raw) <= 1:
        # Single letters, not sure what to do with these?
        # Is this an error?
        return HebUnknown(word=word, raw=raw)

    if raw in HEBREW_PREPOSITIONS:
        return HebPreposition(word=constanants(raw), raw=raw)

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

    if preposition or definite_article:
        return HebVerb(
            preposition=preposition,
            definite_article=definite_article,
            word=constanants(word),
            raw=raw,
        )

    return HebUnknown(word=constanants(word), raw=raw)


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
            count INT
        )"""
    )

    for raw, word in parsed_words.items():
        db.execute(
            "INSERT INTO words VALUES (?,?,?)",
            (raw, word.word, count[word.word]),
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
