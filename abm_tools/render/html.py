"""Render text format"""

from sys import stdout
from typing import Callable, List, TextIO

from abm_tools.sedra.bible import book_name
from abm_tools.sedra.db import parse_sedra3_words_db_file


class RenderBibleHTML:
    """Renderer using plain text HTML format"""

    def __init__(
        self,
        transliterator: Callable[[str], str],
        stream: TextIO = stdout,
    ) -> None:
        """Initialise a text renderer"""
        self._stream = stream
        self._transliterator = transliterator

        self._words_db = parse_sedra3_words_db_file()
        self._words: List[str] = []

        self._book: str = ""
        self._chapter: int = 0
        self._verse: int = 0

    def start_mod(self) -> None:
        """Start the module"""
        print(
            "<html dir='rtl' lang='syr' "
            'style=\'font-family: "Estrangelo Edessa WF", "ExtendedLatinWF"; '
            "font-size: 36px; line-height: 1.2; height: 150px;'>"
            "<head></head><body>",
            file=self._stream,
        )

    def end_mod(self) -> None:
        """End the module"""
        print("</body></html>", file=self._stream)

    def start_book(self, number: int) -> None:
        """Start a new book"""
        self._book = book_name(number)
        print(f"<h1>{self._book}</h1>", file=self._stream)

    def end_book(self) -> None:
        """End the current book"""
        self._book = ""

    def start_chapter(self, number: int) -> None:
        """Start a book chapter"""
        self._chapter = number
        print(f"<h2>Chapter {self._chapter}</h2>", file=self._stream)

    def end_chapter(self) -> None:
        """End the current book chapter"""
        self._chapter = 0

    def start_verse(self, number: int) -> None:
        """Start the verse"""
        self._verse = number

    def end_verse(self) -> None:
        """End the verse"""
        text = " ".join(self._words)
        self._words.clear()

        print(
            f"<p><b>{self._chapter}:{self._verse}</b> {text}</p>",
            file=self._stream,
        )

        self._verse = 0

    def add_word(self, word_id: int) -> None:
        """Add word to the active verse"""
        word = str(self._words_db.loc[word_id, "strVocalised"])

        self._words.append(self._transliterator(word))
