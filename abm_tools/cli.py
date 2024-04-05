"""Aramaic Bible Module tool"""

from pathlib import Path

import click

from abm_tools.sedra.bible import parse_sedra3_bible_db_file
from abm_tools.sedra.db import (
    TRANSLIT_MAPS,
    SEDRAPassageRef,
    book_name,
    from_transliteration,
    parse_sedra3_words_db_file,
    sedra4_db_word_json,
)


@click.group()
def cli():
    """Tools for interacting with SEDRA and generating aramain bible modules"""


@cli.command()
@click.argument("word_id", type=int)
def lookup(word_id: int):
    """Lookup a word in the SEDRA 4 DataBase"""
    print(sedra4_db_word_json(word_id))


@cli.group()
def gen():
    """Tools for generating Aramaic bible software modules"""


@gen.command()
@click.option(
    "-a",
    "--alphabet",
    default="syriac",
    type=click.Choice(TRANSLIT_MAPS.keys(), case_sensitive=False),
)
def bible(alphabet: str):
    """Create Aramaic Sword modules"""

    words_db = parse_sedra3_words_db_file()

    current_ref = SEDRAPassageRef(52, 1, 1)
    words = []

    for book_num, chapter, verse, _, word_id in parse_sedra3_bible_db_file():
        ref = SEDRAPassageRef(book_num, chapter, verse)
        if ref != current_ref:
            text = " ".join(words)

            print(f"{current_ref}) {text}")

            current_ref = ref
            words.clear()

        words.append(
            from_transliteration(
                words_db.loc[word_id]["strVocalised"], alphabet=alphabet
            )
        )


if __name__ == "__main__":
    cli()
