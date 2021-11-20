"""Module to import SEDRA source files
"""
from typing import Generator, Tuple

__all__ = ("parse_sedra3_bible_db_file",)


WordRefTuple = Tuple[int, int, int, int]
WordEntryTuple = Tuple[int, int, int, int, int]


def _parse_sedra3_word_ref(word_ref: str) -> WordRefTuple:
    """Parse word reference string used in the SEDRA3 bible text DB to describe where each word
    occurs in the bible.

    The format of the string is as described in the docs (BFBS.README.TXT):
      - The left 2 digits represent the book (52=Matt, 53=Mark, 54=Luke, etc.)
      - Next 2 digits = chapter
      - Next 3 digits = verse
      - Next 2 digits = word

    So for example 520100101 = Matt, Chapter 1, Verse 1, Word 1

    This is easier to process when transformed into a tuple of integers of the form (book,
    chapter, verse, word).

    Args:
        word_ref: reference string in the format described above.

    Raises:
        AssertionError: when word_ref is empty or isn't 9 characters long
        ValueError: when word_ref contains non integer characters

    Returns:
        Tuple of integers, book, chapter, verse, word. Where book is indexed starting at 52 for
        the gospel of Matthew.
    """
    assert word_ref, "word_ref is not empty"
    assert len(word_ref) == 9, "word_ref is 9 characters long"

    book = int(word_ref[0:2])
    chapter = int(word_ref[2:4])
    verse = int(word_ref[4:7])
    word = int(word_ref[7:9])

    return book, chapter, verse, word


def _parse_sedra3_word_address(word_address: str) -> int:
    """Parse a word address string used in the SEDRA3 bible text DB to point to an entry in the
    tblWords.txt file.

    Essentially the string is a base 10 integer that when converted to hex, the two most
    significant bytes are the "file_number" (a constant of 02h). Once this is stripped from the
    hex number, the remainder is the index of the word being addressed.

    Args:
        word_address: string containing the word address as described above.

    Returns:
        integer id of the word being addressed
    """
    address_as_hex = hex(int(word_address))

    assert address_as_hex[0:3] == "0x2", "SEDRA3 DB FILE_NUMBER is 0x2"

    return int(address_as_hex[3:], 16)


def parse_sedra3_bible_db_file(file_name: str) -> Generator[WordEntryTuple, None, None]:
    """Import a bible text from SEDRA 3 style DB

    Args:
        file_name: file name for the SEDRA3 style bible DB file (BFBS.TXT)

    yield:
        one word entry
    """
    with open(file_name, "r") as bible_file:
        for line in bible_file:
            columns = line.strip().split(",")

            if not columns:
                continue

            # First column is the database address FILE_NUMBER:LINE_NUMBER which is essentially a
            # line number providing no valuable information as I see it right now. Each line
            # contains only one word, and that word is already uniquely addressable via the
            # chapter/verse/word number in the second column (index 1)

            book, chapter, verse, word = _parse_sedra3_word_ref(columns[1])
            word_id = _parse_sedra3_word_address(columns[2])

            yield book, chapter, verse, word, word_id
