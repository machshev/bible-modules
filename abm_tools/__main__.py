"""Aramaic Bible Module tool"""
from pathlib import Path

import click

from abm_tools.sedra.bible import parse_sedra3_bible_db_file
from abm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file, sedra4_db_word_json


@click.group()
def tool():
    """Tools for generating Aramaic bible software modules"""


@tool.command()
@click.argument("word_id", type=int)
def lookup(word_id: int):
    """Lookup a word in the SEDRA 4 DataBase"""
    print(sedra4_db_word_json(word_id))


@tool.command()
@click.argument("file_name", type=click.Path(exists=True))
def gen(file_name: Path) -> int:
    """Create Aramaic Sword modules"""

    words = parse_sedra3_words_db_file()

    for book, chapter, verse, word_num, word_id in parse_sedra3_bible_db_file(
        file_name=str(file_name)
    ):
        #word = from_transliteration(words.loc[word_id]["strVocalised"])
        word = sedra4_db_word_json(word_id)["western"]

        print(
            book,
            chapter,
            verse,
            word_num,
            word_id,
            word,
        )

    return 0
