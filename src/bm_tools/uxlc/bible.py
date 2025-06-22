"""Module to import UXLC bible source files.

UXLC is an XML version of the WLC text.
"""

from collections.abc import Generator, Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.etree.ElementTree import Element, parse

from logzero import logger

from bm_tools.model import BOOKS, Verse, VerseRef

__all__ = ("iterate_verses_ot",)

_BASE_PATH = Path("src_texts/UXLC/Books")


_TanachIndexET: Element | None = None


def _get_tanach_index_element_tree() -> Element:
    """Get the tanach index XML ElementTree from UXLC."""
    global _TanachIndexET  # noqa: PLW0603

    if _TanachIndexET is None:
        et = parse(_BASE_PATH / "TanachIndex.xml")  # noqa: S314
        _TanachIndexET = et.getroot()

    return _TanachIndexET


def _get_book_element_tree(name: str) -> Element:
    """Get a book XML ElementTree from UXLC."""
    filename_element = _get_tanach_index_element_tree().find(
        f".//name[.='{name}']/../filename"
    )
    if filename_element is None:
        logger.fatal("Could not find a book named %s in UXCL", name)
        raise ValueError

    filename = filename_element.text

    path = _BASE_PATH / f"{filename}.xml"

    if not path.is_file():
        logger.warning("Book src text not found: %s", path)
        path = _BASE_PATH / f"{filename}.DH.xml"

    if not path.is_file():
        logger.fatal("Book src text not found: %s", path)
        raise ValueError

    et = parse(path)  # noqa: S314 all files are from a known src

    return et.getroot()


def get_book(name: str) -> list[list[list[str]]]:
    """Get the book text."""
    root = _get_book_element_tree(name=name)

    # Store the parsed data in dict format initially as the parsing order is not
    # neceserily guaranteed.
    chapters = {}

    # Find all chapter elements
    for c in root.findall(".//c"):
        c_num = int(c.attrib["n"])

        chapters[c_num] = {}

        verses = {}
        for v in c.findall("./v"):
            v_num = int(v.attrib["n"])

            words = []
            for w in v.iter():
                if w.tag != "w":
                    continue

                words.append(w.text)

            verses[v_num] = words

        chapters[c_num] = [v for _, v in sorted(verses.items())]

    return [v for _, v in sorted(chapters.items())]


def get_all_books() -> list[list[list[list[str]]]]:
    """Get all the books in UXLC."""
    return [get_book(name=book) for book in BOOKS[:39]]


@dataclass
class VerseUXLC(Verse):
    """New Testement UXLC verse."""

    ref: VerseRef
    words: Sequence[str]


def iterate_verses_ot() -> Generator[VerseUXLC]:
    """Iterate UXLC bible verses."""
    books = get_all_books()
    for book_id, book in enumerate(books):
        for chapter_id, chapter in enumerate(book):
            for verse_id, words in enumerate(chapter):
                yield VerseUXLC(
                    ref=VerseRef(
                        book=book_id + 1,
                        chapter=chapter_id + 1,
                        verse=verse_id + 1,
                    ),
                    words=words,
                )
