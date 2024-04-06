"""Renderer interfaces
"""

from typing import Protocol


class BibleRenderer(Protocol):
    """Protocol used in rendering bibles"""

    def start_book(self, name: str) -> None:
        """Start a new book"""

    def end_book(self) -> None:
        """End the current book"""

    def start_chapter(self, name: str) -> None:
        """Start a book chapter"""

    def end_chapter(self) -> None:
        """End the current book chapter"""

    def start_verse(self, number: int) -> None:
        """Start the verse"""

    def end_verse(self) -> None:
        """End the verse"""
