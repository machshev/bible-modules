"""Renderer interfaces."""

from collections.abc import Iterable
from typing import Protocol

from bm_tools.bible import BibleVerseEntryTuple


class SourceTextReader(Protocol):
    """Protocol used to read bible source texts."""

    def readlines() -> Iterable[BibleVerseEntryTuple]:
        """Read each verse."""


class BibleRenderer(Protocol):
    """Protocol used in rendering bibles."""

    def start_mod(self, name: str) -> None:
        """Start the module."""

    def end_mod(self) -> None:
        """End the module."""

    def start_book(self, number: int) -> None:
        """Start a new book."""

    def end_book(self) -> None:
        """End the current book."""

    def start_chapter(self, number: int) -> None:
        """Start a book chapter."""

    def end_chapter(self) -> None:
        """End the current book chapter."""

    def start_verse(self, number: int) -> None:
        """Start the verse."""

    def end_verse(self) -> None:
        """End the verse."""

    def add_word(self, word_id: int) -> None:
        """Add word to the active verse."""
