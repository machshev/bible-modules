"""Module that contains the command line application."""

# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m bm_tools` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `bm_tools.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `bm_tools.__main__` in `sys.modules`.

from pathlib import Path

import click

from bm_tools.render import _BIBLE_RENDERERS, render_bible
from bm_tools.sedra.bible import gen_bible_cache_file
from bm_tools.sedra.db import TRANSLIT_MAPS, sedra4_db_word_json


@click.group()
def main() -> None:
    """Tools for interacting with SEDRA and generating aramain bible modules."""


@main.command()
@click.argument("word_id", type=int)
def lookup(word_id: int) -> None:
    """Lookup a word in the SEDRA 4 DataBase."""
    click.echo(sedra4_db_word_json(word_id=word_id))


@main.group()
def gen() -> None:
    """Tools for generating Aramaic bible software modules."""


@gen.command()
@click.argument("mod_name", type=str)
@click.argument(
    "output_path",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
)
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
def bible(
    alphabet: str,
    fmt: str,
    output_path: Path,
    mod_name: str,
) -> None:
    """Create Aramaic bible module MOD_NAME in the FORMAT and ALPHABET."""
    render_bible(
        alphabet=alphabet,
        fmt=fmt,
        output_path=output_path,
        mod_name=mod_name,
    )


@gen.command()
def cache_file() -> None:
    """Generate a cache file for easier SEDRA3 bible parsing."""
    gen_bible_cache_file()


if __name__ == "__main__":
    main()
