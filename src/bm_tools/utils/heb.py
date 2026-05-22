"""Hebrew word utility functions."""

import sqlite3
from collections.abc import Mapping
from pathlib import Path

from logzero import logger

from bm_tools.morph import HebUnknown, ParsedWord, morph_eval, normalise

__all__ = (
    "parse_bible",
    "review",
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
    sort: bool = False,
) -> None:
    """Review the morphology results."""
    db_path = Path.cwd() / "modules" / "haqor" / "haqor.db"

    db = sqlite3.connect(db_path)

    query = "SELECT raw FROM words" + (" ORDER BY count DESC" if sort else "")

    for idx, result in enumerate(db.execute(query)):
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
