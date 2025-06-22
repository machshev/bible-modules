"""Module to import SEDRA source files.

After generating modules from the BFBS.TXT file, it turns out there are a few
verses that are out of order in the file. So it's not possible to just assume
each line is part of a series of contiguous lines that make up verses. The whole
file needs to be parsed to ensure all the words in each verse are accounted for.

Given that, we will create an in memory structure containing all of the words in
the peshitta. Making no assumptions on the number of words or the relative
positions. Then post process that data structure to export an intermediate file
that does conform to these basic assumptions. This should speed up multiple
module generation but slow down individual module generation the first time.

Given the source files are not changing, the intermediate format will also be
checked in. Although it should be possible to regenerate it from the original
files.
"""

from collections.abc import Generator, Sequence
from dataclasses import dataclass
from pathlib import Path

from bm_tools.model import Verse, VerseRef
from bm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file

__all__ = (
    "iterate_verses_nt",
    "parse_sedra3_bible_db_file",
)


WordRefTuple = tuple[VerseRef, int]
WordEntryTuple = tuple[VerseRef, int, int]
SEDRA_WORD_REF_LEN: int = 9


def _parse_sedra3_word_ref(word_ref: str) -> WordRefTuple:
    """Parse word reference string used in the SEDRA3 bible text DB.

    The format of the string is as described in the docs (BFBS.README.TXT):
      - The left 2 digits represent the book (52=Matt, 53=Mark, 54=Luke, etc.)
      - Next 2 digits = chapter
      - Next 3 digits = verse
      - Next 2 digits = word

    So for example 520100101 = Matt, Chapter 1, Verse 1, Word 1

    This is easier to process when transformed into a tuple of integers of the
    form (book, chapter, verse, word).

    Args:
        word_ref: reference string in the format described above.

    Raises:
        AssertionError: when word_ref is empty or isn't 9 characters long
        ValueError: when word_ref contains non integer characters

    Returns:
        Tuple of integers, book, chapter, verse, word. Where book is indexed
        starting at 52 for the gospel of Matthew.
    """
    if len(word_ref) != SEDRA_WORD_REF_LEN:
        msg = f"Expected word_ref of {SEDRA_WORD_REF_LEN} characters"
        raise ValueError(msg)

    book = int(word_ref[0:2])
    chapter = int(word_ref[2:4])
    verse = int(word_ref[4:7])
    word = int(word_ref[7:9])

    return VerseRef(book, chapter, verse), word


def _parse_sedra3_word_address(word_address: str) -> int:
    """Parse a word address string used in the SEDRA3 bible text DB.

    Essentially the string is a base 10 integer that when converted to hex, the
    two most significant bytes are the "file_number" (a constant of 02h). Once
    this is stripped from the hex number, the remainder is the index of the word
    being addressed.

    Args:
        word_address: string containing the word address as described above.

    Returns:
        integer id of the word being addressed in the tblWords.txt file
    """
    address_as_hex = hex(int(word_address))

    if address_as_hex[0:3] != "0x2":
        msg = "Expected SEDRA3 DB FILE_NUMBER is 0x2"
        raise ValueError(msg)

    return int(address_as_hex[3:], 16)


def parse_sedra3_bible_db_file(
    file_name: str = "./src_texts/SEDRA/BFBS.TXT",
) -> Generator[WordEntryTuple]:
    """Import a bible text from SEDRA 3 style DB.

    Note: the words on each row are not contiguous. There are words at the end
    of the file that are out of order and this may be the case elsewhere. Don't
    rely or the order of the entries.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (BFBS.TXT)

    Yield:
        one word entry
    """
    with Path(file_name).open(encoding="utf-8") as bible_file:
        for line in bible_file:
            columns = line.strip().split(",")

            if not columns:
                continue

            # First column is the database address FILE_NUMBER:LINE_NUMBER which
            # is essentially a line number providing no valuable information as
            # I see it right now. Each line contains only one word, and that
            # word is already uniquely addressable via the chapter/verse/word
            # number in the second column (index 1)

            ref, word = _parse_sedra3_word_ref(columns[1])
            word_id = _parse_sedra3_word_address(columns[2])

            yield ref, word, word_id


def _create_bible_structure() -> dict:
    """Load the bible model."""
    bible: dict[int, dict[int, dict[int, dict[int, int]]]] = {}

    for ref, word, word_id in parse_sedra3_bible_db_file():
        if ref.book not in bible:
            bible[ref.book] = {}

        book = bible[ref.book]

        if ref.chapter not in book:
            book[ref.chapter] = {}

        chapter = book[ref.chapter]

        if ref.verse not in chapter:
            chapter[ref.verse] = {}

        chapter[ref.verse][word] = word_id

    return bible


def gen_bible_cache_file() -> None:
    """Generate the bible cache file."""
    bible_struct = _create_bible_structure()

    with Path("./src_texts/SEDRA/BFBS.cache").open(mode="w", encoding="utf-8") as f:
        for book_id in sorted(bible_struct.keys()):
            for chapter_id in sorted(bible_struct[book_id].keys()):
                for verse_id in sorted(bible_struct[book_id][chapter_id].keys()):
                    verse_struct = bible_struct[book_id][chapter_id][verse_id]

                    verse_text = " ".join(
                        str(verse_struct[word]) for word in sorted(verse_struct.keys())
                    )

                    f.write(f"{book_id},{chapter_id},{verse_id},{verse_text}\n")


@dataclass
class VerseSEDRA(Verse):
    """New Testement SEDRA verse."""

    ref: VerseRef
    words: Sequence[str]
    word_ids: Sequence[int]

    def transliterate(self, alphabet: str) -> Sequence[str]:
        """Get words."""
        return [from_transliteration(w, alphabet=alphabet) for w in self.words]


def iterate_verses_nt() -> Generator[VerseSEDRA]:
    """Parse the bible cache file."""
    words_db = parse_sedra3_words_db_file()
    cache_path = Path("./src_texts/SEDRA/BFBS.cache")

    if not cache_path.is_file():
        gen_bible_cache_file()

    with cache_path.open(mode="r", encoding="utf-8") as f:
        for line in f:
            book_id, chapter_id, verse_id, text = line.strip().split(",")

            word_ids = text.split(" ")

            yield VerseSEDRA(
                ref=VerseRef(
                    book=int(book_id) - 13,
                    chapter=int(chapter_id),
                    verse=int(verse_id),
                ),
                word_ids=word_ids,
                words=[str(words_db.loc[int(w), "strVocalised"]) for w in word_ids],
            )
