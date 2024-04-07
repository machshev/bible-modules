"""Aramaic Bible Module tool"""

import click

from abm_tools.render import _BIBLE_RENDERERS, get_bible_renderer
from abm_tools.sedra.db import TRANSLIT_MAPS, sedra4_db_word_json


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
    type=click.Choice(_BIBLE_RENDERERS, case_sensitive=False),
)
def bible(alphabet: str, fmt: str):
    """Create Aramaic Sword modules"""
    render = get_bible_renderer(alphabet=alphabet, fmt=fmt)
    render()


if __name__ == "__main__":
    cli()
