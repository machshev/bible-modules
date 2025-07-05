"""Post process a newly generated Haqor bible module db.

The renderer will add the bible text, this module takes that content and add
meta data and indexes.
"""

from sqlite3 import Connection

from logzero import logger

from bm_tools.haqor.verse_complex import gen_verse_complexity
from bm_tools.haqor.word_count import gen_word_count


def post_process(db: Connection) -> None:
    """Post process a new Haqor db.

    Args:
        db: connection to an SQLite3 haqor db.
    """
    logger.info("Post processing Haqor DB")

    word_count = gen_word_count(db=db)
    gen_verse_complexity(db=db, word_count=word_count)
