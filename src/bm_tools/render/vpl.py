"""Render verse per line (VPL) format.

The verse per line format is used by SWORD project for simple modules that don't
need additional formatting. So this module format is just a simple text format
without extra markup.

## Example

```
Genesis 1:1 In the beginning God created the heaven and the earth.
Genesis 1:2 And the earth was without form, and void; and darkness was upon ...
```

"""

from pathlib import Path
from typing import TextIO

from bm_tools.model import Verse, book_name
from bm_tools.sedra.bible import VerseSEDRA


class RenderBibleVPL:
    """Renderer using plain text in VPL format."""

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
        self._stream = (self._output_path / f"{name}.vpl").open(
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
            msg = "Can't start a verse without starting a module"
            raise RuntimeError(msg)

        print(
            f"{self._book} {self._chapter}:{self._verse} {text}",
            file=self._stream,
        )

        self._verse = 0

    def add_words(self, verse: Verse) -> None:
        """Add word to the active verse."""
        if isinstance(verse, VerseSEDRA):
            self._words = verse.transliterate(alphabet=self._alphabet)
        else:
            self._words = verse.words
