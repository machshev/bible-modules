"""Verse complexity rating.

This is useful to rate each verse by how often the words it contains are used.
Which means we can sort the verses on how easy they might be to read.
"""

from collections.abc import Mapping, Sequence
from sqlite3 import Connection

from logzero import logger

from bm_tools.utils.heb import ParsedWord, normalise


def gen_verse_complexity(
    db: Connection,
    parsed_words: Sequence[ParsedWord],
    word_count: Mapping,
) -> None:
    """Generate a verse complexity score.

    Args:
        db: connection to an SQLite3 haqor db.
        parsed_words: sequence of parsed word objects
        word_count: mapping of words to word count.
    """
    logger.info("Calculating verse complexity Haqor DB")

    bible = []
    parse_lookup = {word.raw: word.word for word in parsed_words}

    for result in db.execute(
        "SELECT book, chapter, verse, words FROM hebrew WHERE book <= 39"
    ):
        book, chapter, verse, words = result
        min_count = 999999
        for raw in words.split(" "):
            normalised = normalise(text=raw)

            if not normalised:
                continue

            word = parse_lookup[normalised]
            min_count = min(min_count, word_count[word])

        bible.append((book, chapter, verse, words, min_count))

    logger.info("Add ease column")

    # Add column to store the complexity score
    db.execute("""ALTER TABLE hebrew ADD ease INT""")

    # Seems it is significantly faster to remove the entries and add them in
    # again than do an update.
    db.execute("DELETE FROM hebrew WHERE book <= 39")
    db.executemany(
        "INSERT INTO hebrew VALUES (?,?,?,?,?)",
        bible,
    )

    db.commit()
