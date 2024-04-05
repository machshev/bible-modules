"""Module to import SEDRA DB parser using pandas for all the heavy lifting."""

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests

__all__ = (
    "parse_sedra3_words_db_file",
    "parse_sedra3_english_db_file",
    "parse_sedra3_roots_db_file",
    "parse_sedra3_lexemes_db_file",
    "sedra4_db_word_json",
    "from_transliteration",
)

HEBREW = {
    "A": "א",
    "B": "ב",
    "G": "ג",
    "D": "ד",
    "H": "ה",
    "O": "ו",
    "Z": "ז",
    "K": "ח",
    "Y": "ט",
    ";": "י",
    "C": "ק",
    "L": "ל",
    "M": "מ",
    "N": "נ",
    "S": "ס",
    "E": "ע",
    "I": "פ",
    "/": "צ",
    "X": "ק",
    "R": "ר",
    "W": "ש",
    "T": "ת",
    # Check
    "'": "ּ",
    ",": "",
    "a": "ַ",
    "e": "ֵ",
    "i": "ִ",
    "o": "ָ",
    "u": "",
    "_": "",
    "-": "-",
    "*": "8",
}

SYRIAC = {
    "A": "ܐ",
    "B": "ܒ",
    "G": "ܓ",
    "D": "ܕ",
    "H": "ܗ",
    "O": "ܘ",
    "Z": "ܙ",
    "K": "ܚ",
    "Y": "ܛ",
    ";": "ܝ",
    "C": "ܟ",
    "L": "ܠ",
    "M": "ܡ",
    "N": "ܢ",
    "S": "ܣ",
    "E": "ܥ",
    "I": "ܦ",
    "/": "ܨ",
    "X": "ܩ",
    "R": "ܪ",
    "W": "ܫ",
    "T": "ܬ",
    # Check
    "'": "݁",
    ",": "݂",
    "a": "ܱ",
    "e": "",
    "i": "ܻ",
    "o": "",
    "u": "",
    "_": "_",
    "-": "-",
    "*": "̈",
}

BOOKS = (
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

TRANSLIT_MAPS = {
    "syriac": SYRIAC,
    "hebrew": HEBREW,
}


@dataclass
class SEDRAPassageRef:
    """SEDRA bible db passage reference"""

    book: int
    chapter: int
    verse: int

    def __str__(self) -> str:
        """Human readable string"""
        book = book_name(self.book)

        return f"{book} {self.chapter}:{self.verse}"


def book_name(book_num: int) -> str:
    """Book name given a book number"""
    return BOOKS[book_num - 52]


def sedra4_db_word_json(word_id: int):
    """Request word lookup from SEDRA4 DB."""
    word_json_path = Path(f"words/{word_id}.json")

    # Use cache version if it exists
    if word_json_path.is_file():
        with word_json_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)

    word_json_path.parent.mkdir(parents=True, exist_ok=True)

    json_result = requests.get(
        f"https://sedra.bethmardutho.org/api/word/{word_id}.json",
        timeout=100,
    ).json()[0]

    word_json_path.write_text(json.dumps(json_result), encoding="utf-8")

    return json_result


def from_transliteration(string: str, alphabet: str) -> str:
    """Convert transliteration string to unicode Aramaic.

    Args:
        string: the string to convert

    Returns:
        Converted string
    """
    if alphabet not in TRANSLIT_MAPS:
        valid_alphabets = TRANSLIT_MAPS.keys()
        raise ValueError(
            f"alphabet must be one of {valid_alphabets} not '{alphabet}'",
        )

    return "".join(list(map(lambda c: TRANSLIT_MAPS[alphabet][c], string)))


def parse_sedra3_words_db_file(file_name: str = "SEDRA/tblWords.txt") -> pd.DataFrame:
    """Import a words db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style words DB file (tblWords.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    words = pd.read_csv(file_name, index_col="keyWord")

    return words


def parse_sedra3_english_db_file(
    file_name: str = "SEDRA/tblEnglish.txt",
) -> pd.DataFrame:
    """Import a english db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblEnglish.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    english = pd.read_csv(file_name, index_col="keyEnglish")

    return english


def parse_sedra3_roots_db_file(file_name: str = "SEDRA/tblRoots.txt") -> pd.DataFrame:
    """Import a roots db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblRoots.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    roots = pd.read_csv(file_name, index_col="keyRoot")

    return roots


def parse_sedra3_lexemes_db_file(
    file_name: str = "SEDRA/tblLexemes.txt",
) -> pd.DataFrame:
    """Import a lexemes db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblLexemes.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    lexemes = pd.read_csv(file_name, index_col="keyLexemes")

    return lexemes
