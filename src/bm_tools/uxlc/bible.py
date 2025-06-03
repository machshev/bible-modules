"""Module to import UXLC bible source files.

UXLC is an XML version of the WLC text.
"""

from pathlib import Path
from xml.etree.ElementTree import Element, parse

from logzero import logger

_BASE_PATH = Path("src_texts/UXLC/Books")
BOOKS = ("Genesis", "Exodus")


def _get_book_element_tree(name: str) -> Element:
    """Get a book XML ElementTree from UXLC."""
    path = _BASE_PATH / f"{name}.xml"

    if not path.is_file():
        logger.warning("Book src text not found: %s", path)
        path = _BASE_PATH / f"{name}.DH.xml"

    if not path.is_file():
        logger.fatal("Book src text not found: %s", path)
        raise ValueError

    et = parse(path)  # noqa: S314 all files are from a known src

    return et.getroot()


def get_book(name: str) -> dict[int, dict[int, list[str]]]:
    """Get the book text."""
    root = _get_book_element_tree(name=name)

    chapters = {}

    # Find all chapter elements
    for c in root.findall(".//c"):
        c_num = c.attrib["n"]

        chapters[c_num] = {}

        for v in c.findall("./v"):
            v_num = v.attrib["n"]

            words = []
            for w in v.iter():
                if w.tag != "w":
                    continue

                words.append(w.text)

            chapters[c_num][v_num] = words

    return chapters
