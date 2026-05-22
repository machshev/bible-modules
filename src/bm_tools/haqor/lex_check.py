"""Check BDB lexicon coverage for every word in the bible."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from logzero import logger

__all__ = ("lex_check",)


@dataclass
class _MissingEntry:
    raw: str
    consonants: str
    count: int


def lex_check(*, db_path: Path, num: int | None) -> None:
    """Check that every word in the bible has a BDB entry.

    Iterates through all word types in the ``words`` table, queries the ``bdb``
    table by consonants, and prints a summary of words with no match.

    Args:
        db_path: path to ``haqor.db``.
        num: maximum number of missing words to print (None = all).
    """
    db = sqlite3.connect(db_path)

    # Verify the bdb table exists
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    if "bdb" not in tables:
        logger.error(
            "No 'bdb' table found in %s. Run `bm admin import-bdb` first.",
            db_path,
        )
        return
    if "words" not in tables:
        logger.error(
            "No 'words' table found in %s. Generate the module first.",
            db_path,
        )
        return

    missing: list[_MissingEntry] = []
    total = 0

    for raw, consonants, count in db.execute(
        "SELECT raw, constanants, count FROM words ORDER BY count DESC"
    ):
        total += 1
        hit = db.execute(
            "SELECT 1 FROM bdb WHERE consonants = ? LIMIT 1", (consonants,)
        ).fetchone()
        if hit is None:
            missing.append(_MissingEntry(raw=raw, consonants=consonants, count=count))

    db.close()

    covered = total - len(missing)
    pct = covered / total * 100 if total else 0
    logger.info(
        "Checked %d word types: %d have a BDB entry (%.1f%%), %d do not",
        total,
        covered,
        pct,
        len(missing),
    )

    shown = missing if num is None else missing[:num]

    if not shown:
        logger.info("All words have a BDB entry.")
        return

    logger.info("Words without a BDB entry (showing %d of %d):", len(shown), len(missing))
    for entry in shown:
        # Print word right-to-left reversed so it displays correctly in terminals
        print(f"  {entry.consonants:<12}  count={entry.count:>6}  raw={entry.raw}")
