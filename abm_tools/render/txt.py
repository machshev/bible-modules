"""Render text format"""

from sys import stdout
from typing import TextIO


class RenderBibleText:
    """Renderer using plain text"""

    def __init__(self, stream: TextIO = stdout) -> None:
        """Initialise a text renderer"""
        self._stream = stream

    def start_book(self, name: str) -> None:
        """Start a new book"""
        print(f"# {name}", file=self._stream)

    def end_book(self) -> None:
        """End the current book"""
