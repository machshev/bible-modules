"""Renderer interfaces
"""

from typing import Protocol


class BibleRenderer(Protocol):
    """Protocol used in rendering bibles"""

    def start_mod(self, name: str) -> None:
        """Start the module"""

    def end_mod(self) -> None:
        """End the module"""

    def start_book(self, number: int) -> None:
        """Start a new book"""

    def end_book(self) -> None:
        """End the current book"""

    def start_chapter(self, number: int) -> None:
        """Start a book chapter"""

    def end_chapter(self) -> None:
        """End the current book chapter"""

    def start_verse(self, number: int) -> None:
        """Start the verse"""

    def end_verse(self) -> None:
        """End the verse"""

    def add_word(self, word_id: int) -> None:
        """Add word to the active verse"""
