"""Render OSIS 2.1 format.

From OSIS format it's possible to generate SWORD modules. Crosswire don't
provide documentation of the SWORD module format, instead require people to
depend on the SWORD API. There are alternatives that provide unofficial support
for directly reading and writing SWORD modules, but this may break any time if
the underlying format changes.

For the moment, for these reasons this format is the preferred way to generate
SWORD modules using (osis2mod)[https://wiki.crosswire.org/Osis2mod].

TODO: update the Makefile to postprocess this module format and generate SWORD
modules using the official tools. I'm not fully comfortable with this as we need
to find a way of doing that without depending on arbitrary binaries.
"""

from pathlib import Path
from typing import TextIO

from abm_tools.sedra.bible import book_name
from abm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file

# ruff: noqa: TRY003


class RenderBibleOSIS:
    """Renderer using plain text in OSIS format."""

    def __init__(
        self,
        output_path: Path,
        alphabet: str = "syriac",
    ) -> None:
        """Initialise a text renderer."""
        self._output_path = output_path
        self._stream: TextIO | None = None
        self._alphabet = alphabet

        self._words: list[str] = []

        self._book: str = ""
        self._chapter: int = 0
        self._verse: int = 0

    def start_mod(self, name: str) -> None:
        """Start the module."""
        self._stream = (self._output_path / f"{name}.osis").open(
            mode="w",
            encoding="utf-8",
        )

    def end_mod(self) -> None:
        """End the module."""
        if self._stream is None:
            return

        self._stream.close()

    def start_book(self, number: int) -> None:
        """Start a new book."""
        self._book = book_name(number)

    def end_book(self) -> None:
        """End the current book."""
        self._book = ""

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
        text = " ".join(self._words)
        self._words.clear()

        if self._stream is None:
            raise RuntimeError("Can't start a verse without starting a module")

        print(
            f"{self._book} {self._chapter}:{self._verse} {text}",
            file=self._stream,
        )

        self._verse = 0

    def add_word(self, word_id: int) -> None:
        """Add word to the active verse."""
        words_db = parse_sedra3_words_db_file()
        word = str(words_db.loc[word_id, "strVocalised"])

        self._words.append(from_transliteration(word, alphabet=self._alphabet))
