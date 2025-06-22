"""Render Markdown format."""

from pathlib import Path
from typing import TextIO

from bm_tools.model import Verse, book_name
from bm_tools.sedra.bible import VerseSEDRA


class RenderBibleMarkdown:
    """Renderer using plain text in Markdown format."""

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
        self._stream = (self._output_path / f"{name}.md").open(
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

        if self._stream is None:
            msg = "Can't start a book without starting a module"
            raise RuntimeError(msg)

        print(f"# {self._book}\n", file=self._stream)

    def end_book(self) -> None:
        """End the current book."""
        self._book = ""

    def start_chapter(self, number: int) -> None:
        """Start a book chapter."""
        self._chapter = number

        if self._stream is None:
            msg = "Can't start a chapter without starting a module"
            raise RuntimeError(msg)

        print(f"## Chapter {self._chapter}\n", file=self._stream)

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
            msg = "Can't start a verse without starting a module"
            raise RuntimeError(msg)

        print(
            f"&#x202b;*{self._verse}* {text}\n",
            file=self._stream,
        )

        self._verse = 0

    def add_words(self, verse: Verse) -> None:
        """Add word to the active verse."""
        if isinstance(verse, VerseSEDRA):
            self._words = verse.transliterate(alphabet=self._alphabet)
        else:
            self._words = verse.words
