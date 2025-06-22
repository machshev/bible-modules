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

from bm_tools.model import Verse, book_name
from bm_tools.sedra.bible import VerseSEDRA
from bm_tools.templates import get_template

BOOK_ABREV = {
    "Genesis": "Gen",
    "Exodus": "Exo",
    "Leviticus": "Lev",
    "Numbers": "Num",
    "Deuteronomy": "Deut",
    "Joshua": "Josh",
    "Judges": "Judge",
    "1 Samuel": "1Sam",
    "2 Samuel": "2Sam",
    "1 Kings": "1Kings",
    "2 Kings": "2Kings",
    "Isaiah": "Isa",
    "Jeremiah": "Jer",
    "Ezekiel": "Ezk",
    "Hosea": "Hos",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obadiah": "Obd",
    "Jonah": "Jon",
    "Micah": "Mic",
    "Nahum": "Nah",
    "Habakkuk": "Hab",
    "Zephaniah": "Zeph",
    "Haggai": "Hag",
    "Zechariah": "zech",
    "Malachi": "Mal",
    "Psalms": "Psa",
    "Proverbs": "Prov",
    "Job": "Job",
    "Song of Songs": "Song",
    "Ruth": "Ruth",
    "Lamentations": "Lam",
    "Ecclesiastes": "Ecc",
    "Esther": "Est",
    "Daniel": "Dan",
    "Ezra": "Ezr",
    "Nehemiah": "Neh",
    "1 Chronicles": "1Chr",
    "2 Chronicles": "2Chr",
    "Matthew": "Matt",
    "Mark": "Mark",
    "Luke": "Luke",
    "John": "John",
    "Acts": "Acts",
    "Romans": "Rom",
    "1 Corinthians": "1Cor",
    "2 Corinthians": "2Cor",
    "Galatians": "Gal",
    "Ephesians": "Eph",
    "Philippians": "Phil",
    "Colossians": "Col",
    "1 Thessalonians": "1Thess",
    "2 Thessalonians": "2Thess",
    "1 Timothy": "1Tim",
    "2 Timothy": "2Tim",
    "Titus": "Titus",
    "Philemon": "Phlm",
    "Hebrews": "Heb",
    "James": "Jas",
    "1 Peter": "1Pet",
    "2 Peter": "2Pet",
    "1 John": "1John",
    "2 John": "2John",
    "3 John": "3John",
    "Jude": "Jude",
    "Revelation": "Rev",
}


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

        self._book: str = ""
        self._chapter: int = 0
        self._verse: int = 0

    def start_mod(self, name: str) -> None:
        """Start the module."""
        self._stream = (self._output_path / f"{name}.osis.xml").open(
            mode="w",
            encoding="utf-8",
        )

        print(
            get_template("osis/bible_header.osis.jinja2").render(
                osis_work=name,
                osis_id=name,
                title="Peshitta (BFBS text)",
                lang=self._alphabet,
            ),
            file=self._stream,
        )

    def end_mod(self) -> None:
        """End the module."""
        if self._stream is None:
            return

        print(
            get_template("osis/bible_footer.osis.jinja2").render(),
            file=self._stream,
        )

        self._stream.close()

    def start_book(self, number: int) -> None:
        """Start a new book."""
        title = book_name(number)
        self._book = BOOK_ABREV[title]

        print(
            get_template("osis/bible_book_start.osis.jinja2").render(
                book_title=title,
                book_id=self._book,
            ),
            file=self._stream,
        )

    def end_book(self) -> None:
        """End the current book."""
        print(
            get_template("osis/bible_book_end.osis.jinja2").render(
                book_id=self._book,
            ),
            file=self._stream,
        )

        self._book = ""

    def start_chapter(self, number: int) -> None:
        """Start a book chapter."""
        self._chapter = number
        print(
            get_template("osis/bible_chapter_start.osis.jinja2").render(
                book_id=self._book,
                chapter_id=self._chapter,
            ),
            file=self._stream,
        )

    def end_chapter(self) -> None:
        """End the current book chapter."""
        print(
            get_template("osis/bible_chapter_end.osis.jinja2").render(
                book_id=self._book,
                chapter_id=self._chapter,
            ),
            file=self._stream,
        )
        self._chapter = 0

    def start_verse(self, number: int) -> None:
        """Start the verse."""
        self._verse = number

        if self._stream is None:
            msg = "Can't start a verse without starting a module"
            raise RuntimeError(msg)

        ref = f"{self._book}.{self._chapter}.{self._verse}"

        print(
            f'<verse osisID="{ref}"/>',
            file=self._stream,
        )

    def end_verse(self) -> None:
        """End the verse."""
        if self._stream is None:
            msg = "Can't start a verse without starting a module"
            raise RuntimeError(msg)

        ref = f"{self._book}.{self._chapter}.{self._verse}"

        print(f'<verse eID="{ref}"/>', file=self._stream)

        self._verse = 0

    def add_words(self, verse: Verse) -> None:
        """Add word to the active verse."""
        if isinstance(verse, VerseSEDRA):
            words = verse.transliterate(alphabet=self._alphabet)
            for word_id, word in zip(verse.word_ids, words, strict=True):
                print(
                    f'<w lemma="sedra3:{word_id} sedra4:{word_id}">{word}</w>',
                    file=self._stream,
                )

            return

        for word in verse.words:
            print(f"<w>{word}</w>", file=self._stream)
