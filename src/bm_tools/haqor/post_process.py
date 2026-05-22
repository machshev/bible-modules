"""Post process a newly generated Haqor bible module db.

The renderer will add the bible text, this module takes that content and add
meta data and indexes.
"""

from pathlib import Path
from sqlite3 import Connection

from logzero import logger

from bm_tools.haqor.bdb_merge import merge_bdb_cache
from bm_tools.haqor.verse_complex import gen_verse_complexity
from bm_tools.haqor.word_count import save_word_count
from bm_tools.utils.heb import parse_bible

__all__ = ("post_process",)


def post_process(db: Connection, bdb_cache_path: Path | None = None) -> None:
    """Post process a new Haqor db.

    Args:
        db: connection to an SQLite3 haqor db.
        bdb_cache_path: path to the BDB cache DB produced by
            ``bm admin import-bdb``.  When *None* the BDB merge step is
            skipped.
    """
    logger.info("Post processing Haqor DB")

    parsed_words, count = parse_bible(db=db)

    save_word_count(db=db, count=count)

    gen_verse_complexity(db=db, parsed_words=parsed_words, word_count=count)

    if bdb_cache_path is not None:
        merge_bdb_cache(db=db, cache_path=bdb_cache_path)
