"""Word count generation."""

from sqlite3 import Connection

from logzero import logger

from bm_tools.utils.heb import constanants


def gen_word_count(db: Connection) -> dict[str, int]:
    """Generate a word count.

    Args:
        db: connection to an SQLite3 haqor db.
    """
    count = {}

    for words in db.execute("SELECT words FROM hebrew WHERE book <= 39"):
        for raw in words[0].split(" "):
            word = constanants(text=raw)

            if not word:
                continue

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
