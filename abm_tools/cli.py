"""Aramaic Bible Module tool"""

from typing import List

import click

from abm_tools.render import _BIBLE_RENDERERS
from abm_tools.sedra.bible import SEDRAPassageRef, parse_sedra3_bible_db_file
from abm_tools.sedra.db import (
    TRANSLIT_MAPS,
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
    type=click.Choice(list(TRANSLIT_MAPS.keys()), case_sensitive=False),
)
@click.option(
    "-f",
    "--format",
    "fmt",
    default="txt",
    type=click.Choice(list(_BIBLE_RENDERERS.keys()), case_sensitive=False),
)
def bible(alphabet: str, fmt: str):
    """Create Aramaic Sword modules"""

    words_db = parse_sedra3_words_db_file()

    current_ref = SEDRAPassageRef(52, 1, 1)
    words: List[str] = []

    for ref, _, word_id in parse_sedra3_bible_db_file():
        if ref != current_ref:
            text = " ".join(words)

            print(f"{current_ref}) {text}")

            current_ref = ref
            words.clear()

        words.append(
            from_transliteration(
                str(words_db.loc[word_id, "strVocalised"]),
                alphabet=alphabet,
            )
        )


if __name__ == "__main__":
    cli()
