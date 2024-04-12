"""Render text format."""

import importlib
from pathlib import Path
from typing import TextIO

from abm_tools.sedra.bible import book_name
from abm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file

# ruff: noqa: TRY003


class RenderBibleHTML:
    """Renderer using plain text HTML format."""

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
        base_path = self._output_path / name
        base_path.mkdir(parents=True, exist_ok=True)

        resources_path = base_path / "resources"
        resources_path.mkdir(parents=True, exist_ok=True)

        resource_trav = importlib.resources.files(
            "abm_tools.templates.html.resources",
        )

        for file in resource_trav.iterdir():
            (resources_path / file.name).write_bytes(file.read_bytes())

        self._stream = (base_path / "index.html").open(mode="w", encoding="utf-8")
        lang = {"syriac": "syr", "hebrew": "heb"}[self._alphabet]

        css = (
            '<meta content="text/html;charset=utf-8" http-equiv="Content-Type">'
            '<meta content="utf-8" http-equiv="encoding">'
            f"<link rel='stylesheet' href='resources/{lang}.css'>"
        )

        print(
            f"<html dir='rtl' lang='{lang}'>{css}<head></head><body>",
            file=self._stream,
        )

    def end_mod(self) -> None:
        """End the module."""
        if self._stream is None:
            raise RuntimeError("Can't end module without starting it")

        print("</body></html>", file=self._stream)

        self._stream.close()

    def start_book(self, number: int) -> None:
        """Start a new book."""
        self._book = book_name(number)

        if self._stream is None:
            raise RuntimeError("Can't start a book without starting a module")

        print(f"<h1>{self._book}</h1>", file=self._stream)

    def end_book(self) -> None:
        """End the current book."""
        self._book = ""

    def start_chapter(self, number: int) -> None:
        """Start a book chapter."""
        self._chapter = number

        if self._stream is None:
            raise RuntimeError("Can't start a chapter without starting a module")

        print(f"<h2>Chapter {self._chapter}</h2>", file=self._stream)

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
            f"<p><b>{self._verse}</b> {text}</p>",
            file=self._stream,
        )

        self._verse = 0

    def add_word(self, word_id: int) -> None:
        """Add word to the active verse."""
        words_db = parse_sedra3_words_db_file()
        word = str(words_db.loc[word_id, "strVocalised"])

        self._words.append(from_transliteration(word, alphabet=self._alphabet))
