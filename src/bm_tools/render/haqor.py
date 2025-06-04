"""Render Haqor SQLite format."""

import sqlite3
from pathlib import Path

from logzero import logger

from bm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file


class RenderBibleHaqor:
    """Renderer using Haqor SQLite format."""

    def __init__(
        self,
        output_path: Path,
    ) -> None:
        """Initialise a text renderer."""
        self._output_path = output_path
        self._db: sqlite3.Connection | None = None

        self._words_syr: list[str] = []
        self._words_heb: list[str] = []

        self._book: int | None = None
        self._chapter: int = 0
        self._verse: int = 0

    def start_mod(self, name: str) -> None:
        """Start the module."""
        db_path = self._output_path / "haqor.db"

        # remove existing db file
        db_path.unlink(missing_ok=True)

        self._db = sqlite3.connect(db_path)
        self._db.execute(
            """CREATE TABLE syriac(
                book INT,
                chapter INT,
                verse INT,
                words TEXT
            )"""
        )
        self._db.execute(
            """CREATE TABLE hebrew(
                book INT,
                chapter INT,
                verse INT,
                words TEXT
            )"""
        )

    def end_mod(self) -> None:
        """End the module."""
        if self._db:
            self._db.commit()
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
        syr = " ".join(self._words_syr)
        self._words_syr.clear()

        heb = " ".join(self._words_heb)
        self._words_heb.clear()

        if self._db is None:
            msg = "Can't start a verse without starting a module"
            raise RuntimeError(msg)

        logger.debug("%s %s:%s %s", self._book, self._chapter, self._verse, syr)
        logger.debug("%s %s:%s %s", self._book, self._chapter, self._verse, heb)

        self._db.execute(
            "INSERT INTO syriac VALUES (?,?,?,?)",
            (self._book, self._chapter, self._verse, syr),
        )

        self._db.execute(
            "INSERT INTO hebrew VALUES (?,?,?,?)",
            (self._book, self._chapter, self._verse, heb),
        )

        self._verse = 0

    def add_word(self, word_id: int) -> None:
        """Add word to the active verse."""
        words_db = parse_sedra3_words_db_file()
        word = str(words_db.loc[word_id, "strVocalised"])

        self._words_syr.append(from_transliteration(word, alphabet="syriac"))
        self._words_heb.append(from_transliteration(word, alphabet="hebrew"))
