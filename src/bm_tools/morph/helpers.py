"""Morphology helpers."""

import sqlite3
from pathlib import Path

from bm_tools.morph.constants import (
    HEBREW_VOWELS,
)


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


def _find_bdb_cache() -> Path | None:
    candidate = Path.cwd() / "modules" / "haqor" / "bdb_cache.db"
    if candidate.exists():
        return candidate
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "modules" / "haqor" / "bdb_cache.db"
        if candidate.exists():
            return candidate
    return None


def load_bdb_noun_lemmas() -> frozenset[str]:
    """Load noun/adjective consonant lemmas from bdb_cache.db.

    Combines two sources so that both root-extracted forms (from lex_consonants)
    and full headword consonant forms (from bdb) are recognised.  The two differ
    because _root() strips matres lectionis (hiriq-yod, holam-vav, etc.) when
    building lex_consonants, whereas inflected words in the corpus keep those
    letters.  Including the headword consonant form lets words like כּוֹכָב
    (kochav → cons כוכב) be found even though lex_consonants only has ככב.
    """
    db_path = _find_bdb_cache()
    if db_path is None:
        return frozenset()
    try:
        db = sqlite3.connect(db_path)
        roots = {
            r[0]
            for r in db.execute(
                "SELECT root FROM lex_consonants WHERE pos IN ('n', 'adj')"
            ).fetchall()
        }
        headwords = {
            constanants(r[0])
            for r in db.execute(
                "SELECT headword FROM bdb WHERE pos IN ('n', 'adj')"
            ).fetchall()
            if r[0]
        }
        db.close()
        return frozenset(roots | headwords)
    except sqlite3.Error:
        return frozenset()
