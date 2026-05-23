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

import os
from pathlib import Path

import click
from click.shell_completion import CompletionItem, FishComplete, add_completion_class
from logzero import INFO, logger, loglevel

loglevel(INFO)

# Hardcoded here to avoid importing heavy modules at CLI load time (shell completion).
_BIBLE_RENDERERS = ["txt", "vpl", "md", "html", "osis", "haqor"]
_TRANSLIT_MAP_KEYS = ["syriac", "hebrew"]


# Click 8.x fish completions are broken: the template uses `string split \n`
# (real newline in fish) but format_completion emits real newlines as field
# separators, so fish array-splits them and each $completion is a bare type
# string with no value. Fix: use tab-separated format and write our own script.
@add_completion_class
class _FixedFishComplete(FishComplete):
    name = "fish"

    def format_completion(self, item: CompletionItem) -> str:
        help_ = (item.help or "_").replace("\t", " ").replace("\n", " ")
        value = item.value.replace("\t", " ").replace("\n", " ")
        return f"{item.type}\t{value}\t{help_}"


@click.group()
def main() -> None:
    """Tools for interacting with src texts and generating bible modules."""


@main.group()
def sedra() -> None:
    """Tools for interacting with the SEDRA db."""


@sedra.command()
@click.argument("word_id", type=int)
def lookup4(word_id: int) -> None:
    """Lookup a word in the SEDRA 4 DataBase."""
    from bm_tools.sedra.db import sedra4_db_word_json
    click.echo(sedra4_db_word_json(word_id=word_id))


@main.group()
def gen() -> None:
    """Tools for generating bible modules."""


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
    type=click.Choice(_TRANSLIT_MAP_KEYS, case_sensitive=False),
)
@click.option(
    "-f",
    "--format",
    "fmt",
    default="txt",
    type=click.Choice(_BIBLE_RENDERERS, case_sensitive=False),
)
def bible(
    *,
    alphabet: str,
    fmt: str,
    output_path: Path,
    mod_name: str,
) -> None:
    """Create a single bible module MOD_NAME in the FORMAT and ALPHABET."""
    from bm_tools.render import render_bible
    render_bible(
        alphabet=alphabet,
        fmt=fmt,
        output_path=output_path,
        mod_name=mod_name,
    )


@gen.command("all")
@click.option(
    "-s",
    "--select",
    "select",
    default=None,
    type=click.Choice(_BIBLE_RENDERERS, case_sensitive=False),
    multiple=True,
    help=(
        "By default all module formats are generated, "
        "this option limits this to the selected module format. "
        "Provided this option multiple times to select multiple "
        "explicit formats (or for more control use the `bm gen bible` "
        "command instead)."
    ),
)
@click.option(
    "--reimport-bdb",
    is_flag=True,
    default=False,
    help="Rebuild the BDB cache (modules/haqor/bdb_cache.db) before generating.",
)
def gen_all(*, select: list[str] | None, reimport_bdb: bool) -> None:
    """Generate all bible modules."""
    from bm_tools.haqor.bdb_import import import_bdb
    from bm_tools.render import render_all
    if reimport_bdb:
        db_path = Path.cwd() / "modules" / "haqor" / "bdb_cache.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.unlink(missing_ok=True)
        count = import_bdb(src_root=Path.cwd(), db_path=db_path)
        logger.info("Wrote %d BDB entries to %s", count, db_path)
    logger.info("Generating all bible modules")
    render_all(select=select)


@main.group()
def admin() -> None:
    """Admin helper tools."""


@main.group()
def haqor() -> None:
    """Haqor tools."""


@haqor.command()
@click.option(
    "-i",
    "--index",
    "index",
    default=0,
    type=int,
    help="Start at index",
)
@click.option(
    "-n",
    "--rows",
    "rows",
    default=None,
    type=int,
    help="How many rows to show",
)
@click.option(
    "-u",
    "--unknowns",
    "unknowns",
    is_flag=True,
    help="Only show unknowns",
)
@click.option(
    "-s",
    "--sort",
    "sort",
    is_flag=True,
    help="Sort by word count descending",
)
def morph_review(*, index: int, rows: int | None, unknowns: bool, sort: bool) -> None:
    """Evaluate morphology."""
    from bm_tools.utils.heb import review
    review(index=index, rows=rows, unknowns=unknowns, sort=sort)


@haqor.group()
def lex() -> None:
    """Lexicon tools."""


@lex.command()
@click.option(
    "-n",
    "--num",
    "num",
    default=20,
    type=int,
    show_default=True,
    help="Number of missing words to print (0 = all)",
)
def check(*, num: int) -> None:
    """Check BDB lexicon coverage for every word in the bible.

    Iterates all word types in haqor.db and reports which ones have no
    matching BDB entry.  Use -n 0 to print every missing word.
    """
    from bm_tools.haqor.lex_check import lex_check
    db_path = Path.cwd() / "modules" / "haqor" / "haqor.db"
    lex_check(db_path=db_path, num=num if num > 0 else None)


@admin.command("install-completions")
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"]),
    default=None,
    help="Target shell (auto-detected from $SHELL if omitted).",
)
def install_completions(*, shell: str | None) -> None:
    """Install shell tab-completions for the bm command."""
    if shell is None:
        shell_path = os.environ.get("SHELL", "")
        for name in ("fish", "zsh", "bash"):
            if name in shell_path:
                shell = name
                break
        else:
            msg = "Could not detect shell; pass --shell bash|zsh|fish"
            raise click.ClickException(msg)

    if shell == "fish":
        dest = Path.home() / ".config" / "fish" / "completions" / "bm.fish"
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Write a custom script rather than using Click's broken fish template.
        # Click 8.x emits real newlines between completion fields, which fish
        # splits into individual array elements, so $metadata[2] is always unset.
        # Our _FixedFishComplete.format_completion uses tabs instead, which fish
        # preserves as-is in array elements and `string split \t` handles cleanly.
        script = (
            "function _bm_completion\n"
            "    set -l response (env _BM_COMPLETE=fish_complete"
            " COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) bm)\n"
            "    for item in $response\n"
            "        set -l parts (string split \\t -- $item)\n"
            "        switch $parts[1]\n"
            "            case plain\n"
            "                if set -q parts[3]; and test $parts[3] != _\n"
            "                    printf '%s\\t%s\\n' $parts[2] $parts[3]\n"
            "                else\n"
            "                    echo $parts[2]\n"
            "                end\n"
            "            case dir\n"
            "                __fish_complete_directories $parts[2]\n"
            "            case file\n"
            "                __fish_complete_path $parts[2]\n"
            "        end\n"
            "    end\n"
            "end\n"
            "\n"
            "complete --no-files --command bm --arguments '(_bm_completion)'\n"
        )
        dest.write_text(script)
        click.echo(f"Installed fish completions → {dest}")
        click.echo("Reload with:  source ~/.config/fish/config.fish")
    else:
        rc_file = Path.home() / (".bashrc" if shell == "bash" else ".zshrc")
        line = f'eval "$(_BM_COMPLETE={shell}_source bm)"\n'
        existing = rc_file.read_text() if rc_file.exists() else ""
        if line.strip() in existing:
            click.echo(f"Completions already present in {rc_file}")
        else:
            with rc_file.open("a") as f:
                f.write(f"\n# bm tab-completions\n{line}")
            click.echo(f"Installed {shell} completions → {rc_file}")
            click.echo(f"Reload with:  source {rc_file}")


@admin.command()
def cache_file() -> None:
    """Generate a cache file for easier SEDRA3 bible parsing."""
    from bm_tools.sedra.bible import gen_bible_cache_file
    gen_bible_cache_file()


@admin.command("import-bdb")
def import_bdb_cmd() -> None:
    """Build the BDB definition cache (modules/haqor/bdb_cache.db).

    This only needs to be re-run when the Sefaria BDB source JSON changes.
    The cache is automatically merged into haqor.db during `bm gen all -s haqor`.
    """
    from bm_tools.haqor.bdb_import import import_bdb
    src_root = Path.cwd()
    db_path = src_root / "modules" / "haqor" / "bdb_cache.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.unlink(missing_ok=True)
    count = import_bdb(src_root=src_root, db_path=db_path)
    logger.info("Wrote %d BDB entries to %s", count, db_path)


if __name__ == "__main__":
    main()
