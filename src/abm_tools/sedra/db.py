"""Module to import SEDRA DB parser using pandas for all the heavy lifting."""

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import requests

from abm_tools.errors import InvalidOptionError

__all__ = (
    "parse_sedra3_words_db_file",
    "parse_sedra3_english_db_file",
    "parse_sedra3_roots_db_file",
    "parse_sedra3_lexemes_db_file",
    "sedra4_db_word_json",
    "from_transliteration",
)

# ruff: noqa: RUF001
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
    "C": "כ",
    "L": "ל",
    "M": "מ",
    "N": "נ",
    "S": "ס",
    "E": "ע",
    "I": "פ",
    "/": "צ",
    "X": "ק",
    "R": "ר",
    "W": "שׁ",
    "T": "ת",
    "'": "ּ",
    "a": "ַ",
    "e": "ֵ",
    "i": "ִ",
    "o": "ָ",
    "u": "ֻ",
}
HEBREW_REPLACEMENTS = {
    ",": "",
    "_": "",
    "-": "",
    "*": "",
    "uO": "וּ",
    "iA": "Ai",
    "D'": "דּ",
    "aD": "Da",
}
HEBREW_FINALS = {
    "צ": "ץ",
    "נ": "ן",
    "כ": "ך",
    "פ": "ף",
    "מ": "ם",
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
SYRIAC_REPLACEMENTS: dict[str, str] = {}
SYRIAC_FINALS: dict[str, str] = {}

TRANSLIT_MAPS = {
    "syriac": (SYRIAC, SYRIAC_REPLACEMENTS, SYRIAC_FINALS),
    "hebrew": (HEBREW, HEBREW_REPLACEMENTS, HEBREW_FINALS),
}


def sedra4_db_word_json(word_id: int) -> dict:
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
        alphabet: the alphabet to use hebrew/syriac

    Returns:
        Converted string
    """
    maps = TRANSLIT_MAPS.get(alphabet)

    if maps is None:
        raise InvalidOptionError(
            name="alphabet",
            options=TRANSLIT_MAPS.keys(),
            value=alphabet,
        )

    translit_map, subs_map, finals_map = maps

    for sub, rep in subs_map.items():
        # switch the pointing from before a vav to after it
        string = string.replace(sub, rep)

    string = "".join([translit_map.get(c, c) for c in string])

    # Replace any final leters with their final forms if there are any
    final = string[-1]
    if final in finals_map:
        string = string[:-1] + finals_map[final]

    return string


@lru_cache(maxsize=2)
def parse_sedra3_words_db_file(file_name: str = "SEDRA/tblWords.txt") -> pd.DataFrame:
    """Import a words db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style words DB file (tblWords.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    return pd.read_csv(file_name, index_col="keyWord")


@lru_cache(maxsize=2)
def parse_sedra3_english_db_file(
    file_name: str = "SEDRA/tblEnglish.txt",
) -> pd.DataFrame:
    """Import a english db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblEnglish.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    return pd.read_csv(file_name, index_col="keyEnglish")


@lru_cache(maxsize=2)
def parse_sedra3_roots_db_file(file_name: str = "SEDRA/tblRoots.txt") -> pd.DataFrame:
    """Import a roots db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblRoots.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    return pd.read_csv(file_name, index_col="keyRoot")


@lru_cache(maxsize=2)
def parse_sedra3_lexemes_db_file(
    file_name: str = "SEDRA/tblLexemes.txt",
) -> pd.DataFrame:
    """Import a lexemes db file from SEDRA 3 style DB as a pandas DataFrame.

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblLexemes.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    return pd.read_csv(file_name, index_col="keyLexemes")
