"""Render Haqor SQLite format."""

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from logzero import logger

from bm_tools.haqor.post_process import post_process
from bm_tools.model import BOOKS, Verse
from bm_tools.sedra.bible import VerseSEDRA

if TYPE_CHECKING:
    from collections.abc import Sequence


class RenderBibleHaqor:
    """Renderer using Haqor SQLite format."""

    def __init__(
        self,
        output_path: Path,
    ) -> None:
        """Initialise a text renderer."""
        self._output_path = output_path
        self._db: sqlite3.Connection | None = None

        self._words_syr: Sequence[str] | None = []
        self._words_heb: Sequence[str] = []

        self._book: int | None = None
        self._chapter: int = 0
        self._verse: int = 0

    def start_mod(self, name: str) -> None:  # noqa: ARG002
        """Start the module."""
        db_path = self._output_path / "haqor.db"

        # remove existing db file
        db_path.unlink(missing_ok=True)

        self._db = sqlite3.connect(db_path)

        # Bible text
        self._db.execute(
            """CREATE TABLE hebrew(
                book INT,
                chapter INT,
                verse INT,
                words TEXT
            )"""
        )
        self._db.execute(
            """CREATE TABLE syriac(
                book INT,
                chapter INT,
                verse INT,
                words TEXT
            )"""
        )

        # Index for bible book names
        self._db.execute(
            """CREATE TABLE books(
                book INT,
                name TEXT
            )"""
        )
        self._db.executemany(
            "INSERT INTO books VALUES (?,?)",
            ((i + 1, name) for i, name in enumerate(BOOKS)),
        )

    def end_mod(self) -> None:
        """End the module."""
        if not self._db:
            logger.error(
                "Haqor DB is not open, can't end the module before starting it"
            )
            raise RuntimeError

        self._db.commit()

        post_process(db=self._db)

        self._db.close()

        logger.info("Module generated")

    def start_book(self, number: int) -> None:
        """Start a new book."""
        self._book = number

    def end_book(self) -> None:
        """End the current book."""
        self._book = None

    def start_chapter(self, number: int) -> None:
        """Start a book chapter."""
        self._chapter = number

    def end_chapter(self) -> None:
        """End the current book chapter."""
        self._chapter = 0

    def start_verse(self, number: int) -> None:
        """Start the verse."""
        self._verse = number

    def end_verse(self) -> None:
        """End the verse."""
        if self._db is None:
            msg = "Can't start a verse without starting a module"
            raise RuntimeError(msg)

        heb = " ".join(self._words_heb)
        self._words_heb.clear()

        logger.debug("%s %s:%s %s", self._book, self._chapter, self._verse, heb)

        self._db.execute(
            "INSERT INTO hebrew VALUES (?,?,?,?)",
            (self._book, self._chapter, self._verse, heb),
        )

        # This only applies to the NT
        if self._words_syr is not None:
            syr = " ".join(self._words_syr)
            self._words_syr.clear()

            logger.debug("%s %s:%s %s", self._book, self._chapter, self._verse, syr)

            self._db.execute(
                "INSERT INTO syriac VALUES (?,?,?,?)",
                (self._book, self._chapter, self._verse, syr),
            )

        self._verse = 0

    def add_words(self, verse: Verse) -> None:
        """Add word to the active verse."""
        if isinstance(verse, VerseSEDRA):
            self._words_syr = verse.transliterate(alphabet="syriac")
            self._words_heb = verse.transliterate(alphabet="hebrew")

        else:
            self._words_syr = None
            self._words_heb = verse.words
