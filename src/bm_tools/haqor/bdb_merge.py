"""Merge the BDB cache DB into a haqor module DB."""

import sqlite3
from pathlib import Path

from logzero import logger

__all__ = ("merge_bdb_cache",)


def merge_bdb_cache(db: sqlite3.Connection, cache_path: Path) -> None:
    """Copy the ``bdb`` table from *cache_path* into *db*.

    The cache is produced by ``bm admin import-bdb`` and lives at
    ``modules/haqor/bdb_cache.db``.  If the file does not exist the step is
    skipped with a warning so that a plain ``bm gen all -s haqor`` still works
    without requiring the cache to be pre-built.
    """
    if not cache_path.exists():
        logger.warning(
            "BDB cache not found at %s — skipping BDB merge. "
            "Run `bm admin import-bdb` to generate it.",
            cache_path,
        )
        return

    logger.info("Merging BDB cache from %s", cache_path)

    db.execute("ATTACH DATABASE ? AS bdb_cache", (str(cache_path),))
    db.execute(
        """
        CREATE TABLE bdb AS
        SELECT headword, root, pos, gloss, content_json
        FROM bdb_cache.bdb
        """
    )
    db.execute("CREATE INDEX bdb_root ON bdb (root)")
    db.execute(
        """
        CREATE TABLE lex_consonants AS
        SELECT root, pos FROM bdb_cache.lex_consonants
        """
    )
    db.execute(
        """
        CREATE TABLE bdb_aramaic AS
        SELECT headword, root, pos, gloss, content_json
        FROM bdb_cache.bdb_aramaic
        """
    )
    db.execute("CREATE INDEX bdb_aramaic_root ON bdb_aramaic (root)")
    db.execute("DETACH DATABASE bdb_cache")

    count = db.execute("SELECT COUNT(*) FROM bdb").fetchone()[0]
    logger.info("Merged %d BDB entries", count)
    aram_count = db.execute("SELECT COUNT(*) FROM bdb_aramaic").fetchone()[0]
    logger.info("Merged %d Aramaic word entries", aram_count)
