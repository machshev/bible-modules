"""Aramaic Bible Module tool"""
from pathlib import Path

import click

from abm_tools.sedra.bible import parse_sedra3_bible_db_file
from abm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file


@click.command()
@click.argument("file_name", type=click.Path(exists=True))
def gen(file_name: Path) -> int:
    """Create Aramaic Sword modules"""

    words = parse_sedra3_words_db_file()

    for book, chapter, verse, word_num, word_id in parse_sedra3_bible_db_file(
        file_name=str(file_name)
    ):
        word = words.loc[word_id]

        print(
            book,
            chapter,
            verse,
            word_num,
            word_id,
            from_transliteration(word["strVocalised"]),
        )

    return 0
