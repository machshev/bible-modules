"""Word count generation."""

from collections.abc import Sequence
from sqlite3 import Connection

from logzero import logger

from bm_tools.utils.heb import ParsedWord


def gen_word_count(
    db: Connection,
    parsed_words: Sequence[ParsedWord],
) -> dict[str, int]:
    """Generate a word count.

    Args:
        db: connection to an SQLite3 haqor db.
        parsed_words: sequence of parsed word objects
    """
    count = {}

    for parsed in parsed_words:
        word = parsed.word
        if word not in count:
            count[word] = 0

        count[word] += 1

    logger.info("Saving word count to Haqor DB")

    db.execute(
        """CREATE TABLE words(
            word TEXT,
            count INT
        )"""
    )

    for word, c in count.items():
        db.execute(
            "INSERT INTO words VALUES (?,?)",
            (word, c),
        )

    db.commit()

    return count
