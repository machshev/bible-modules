"""Module to import SEDRA DB parser using pandas for all the heavy lifting."""
import json

import pandas as pd
import requests
from pathlib import Path

__all__ = (
    "parse_sedra3_words_db_file",
    "parse_sedra3_english_db_file",
    "parse_sedra3_roots_db_file",
    "parse_sedra3_lexemes_db_file",
    "sedra4_db_word_json",
    "from_transliteration",
)


ESTRANGELA = {
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


def sedra4_db_word_json(word_id: int):
    """Request word lookup from SEDRA4 DB."""
    word_json_path = Path(f"words/{word_id}.json")

    # Use cache version if it exists
    if word_json_path.is_file():
        with word_json_path.open("r") as json_file:
            return json.load(json_file)

    word_json_path.parent.mkdir(parents=True, exist_ok=True)

    json_result = requests.get(
        f"https://sedra.bethmardutho.org/api/word/{word_id}.json"
    ).json()[0]

    word_json_path.write_text(json.dumps(json_result))

    return json_result


def from_transliteration(string: str) -> str:
    """Convert transliteration string to unicode Aramaic.

    Args:
        string: the string to convert

    Returns:
        Converted string
    """
    return "".join(list(map(lambda c: ESTRANGELA[c], string)))


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
