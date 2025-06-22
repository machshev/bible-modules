"""Common data models."""

from collections.abc import Sequence
from dataclasses import dataclass

__all__ = (
    "VerseRef",
    "book_name",
)


BOOKS = (
    # OT
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "Isaiah",
    "Jeremiah",
    "Ezekiel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Psalms",
    "Proverbs",
    "Job",
    "Song of Songs",
    "Ruth",
    "Lamentations",
    "Ecclesiastes",
    "Esther",
    "Daniel",
    "Ezra",
    "Nehemiah",
    "1 Chronicles",
    "2 Chronicles",
    # NT
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
)


def book_name(book_num: int) -> str:
    """Book name given a book number."""
    return BOOKS[book_num]


@dataclass
class VerseRef:
    """Verse reference using raw UXLC and SEDRA book orders."""

    book: int
    chapter: int
    verse: int

    def __str__(self) -> str:
        """Human readable string."""
        book = book_name(self.book)

        return f"{book} {self.chapter}:{self.verse}"


class Verse:
    """Represent a verse."""

    ref: VerseRef
    words: Sequence[str]
