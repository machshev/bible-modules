"""Word count generation."""

from collections.abc import Mapping
from sqlite3 import Connection

from logzero import logger

from bm_tools.utils.heb import ParsedWord

__all__ = ("save_word_count",)


def save_word_count(
    db: Connection,
    count: Mapping[str, ParsedWord],
) -> None:
    """Save the word count to the DB.

    Args:
        db: connection to an SQLite3 haqor db.
        count: mapping of words to occorance count
    """
    logger.info("Saving word count to Haqor DB")

    db.execute(
        """CREATE TABLE count(
            word TEXT,
            count INT
        )"""
    )

    for word, c in count.items():
        db.execute(
            "INSERT INTO count VALUES (?,?)",
            (word, c),
        )

    db.commit()
