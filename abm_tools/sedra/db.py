"""Module to import SEDRA DB parser using pandas for all the heavy lifting
"""
import pandas as pd


__all__ = (
    'parse_sedra3_words_db_file',
    'parse_sedra3_english_db_file',
    'parse_sedra3_roots_db_file',
    'parse_sedra3_lexemes_db_file',
)


def parse_sedra3_words_db_file(file_name: str = 'SEDRA/tblWords.txt') -> pd.DataFrame:
    """Import a words db file from SEDRA 3 style DB as a pandas DataFrame

    Args:
        file_name: file name for the SEDRA3 style words DB file (tblWords.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    words = pd.read_csv(file_name, index_col='keyWord')

    return words


def parse_sedra3_english_db_file(file_name: str = 'SEDRA/tblEnglish.txt') -> pd.DataFrame:
    """Import a english db file from SEDRA 3 style DB as a pandas DataFrame

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblEnglish.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    english = pd.read_csv(file_name, index_col='keyEnglish')

    return english


def parse_sedra3_roots_db_file(file_name: str = 'SEDRA/tblRoots.txt') -> pd.DataFrame:
    """Import a english db file from SEDRA 3 style DB as a pandas DataFrame

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblRoots.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    roots = pd.read_csv(file_name, index_col='keyRoot')

    return roots


def parse_sedra3_lexemes_db_file(file_name: str = 'SEDRA/tblLexemes.txt') -> pd.DataFrame:
    """Import a english db file from SEDRA 3 style DB as a pandas DataFrame

    Args:
        file_name: file name for the SEDRA3 style bible DB file (tblLexemes.txt)

    Returns:
        pandas DataFrame of the words DB table
    """
    lexemes = pd.read_csv(file_name, index_col='keyLexemes')

    return lexemes
