"""Post process a newly generated Haqor bible module db.

The renderer will add the bible text, this module takes that content and add
meta data and indexes.
"""

from sqlite3 import Connection

from logzero import logger

from bm_tools.haqor.verse_complex import gen_verse_complexity
from bm_tools.haqor.word_count import gen_word_count
from bm_tools.utils.heb import morph_eval, normalise


def post_process(db: Connection) -> None:
    """Post process a new Haqor db.

    Args:
        db: connection to an SQLite3 haqor db.
    """
    logger.info("Post processing Haqor DB")

    parsed_words = []

    for result in db.execute("SELECT words FROM hebrew WHERE book <= 39"):
        for raw in result[0].split(" "):
            normalised = normalise(text=raw)

            if not normalised:
                continue

            word = morph_eval(raw=normalised)
            parsed_words.append(word)

    word_count = gen_word_count(
        db=db,
        parsed_words=parsed_words,
    )
    gen_verse_complexity(db=db, parsed_words=parsed_words, word_count=word_count)
