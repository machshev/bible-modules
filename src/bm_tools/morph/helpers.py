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
    """Load noun/adjective consonant lemmas from bdb_cache.db."""
    db_path = _find_bdb_cache()
    if db_path is None:
        return frozenset()
    try:
        db = sqlite3.connect(db_path)
        rows = db.execute("SELECT consonants FROM noun_consonants").fetchall()
        db.close()
        return frozenset(r[0] for r in rows)
    except sqlite3.Error:
        return frozenset()
