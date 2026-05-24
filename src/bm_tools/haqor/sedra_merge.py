"""Merge the SEDRA3 lexicon into a haqor module DB."""

import sqlite3
from pathlib import Path

from logzero import logger

from bm_tools.sedra.db import (
    from_transliteration,
    parse_sedra3_english_db_file,
    parse_sedra3_lexemes_db_file,
    parse_sedra3_roots_db_file,
)

__all__ = ("merge_sedra_lexicon",)

_SEDRA_SRC = Path("src_texts/SEDRA")


def _translit(s: str) -> str:
    if not s:
        return s
    try:
        return from_transliteration(s, alphabet="hebrew")
    except (KeyError, IndexError):
        return s


def merge_sedra_lexicon(
    db: sqlite3.Connection,
    src: Path = _SEDRA_SRC,
) -> None:
    """Create and populate the ``sedra`` table in *db*.

    Schema:
      key_lexeme INTEGER PRIMARY KEY  — SEDRA3 lexeme ID
      lexeme     TEXT                 — Syriac Unicode form
      root       TEXT                 — root in Syriac Unicode
      meaning    TEXT                 — first English gloss (may be empty)
    """
    lexemes_df = parse_sedra3_lexemes_db_file(str(src / "tblLexemes.txt"))
    roots_df = parse_sedra3_roots_db_file(str(src / "tblRoots.txt"))
    english_df = parse_sedra3_english_db_file(str(src / "tblEnglish.txt"))

    first_meaning: dict[int, str] = {}
    for _, eng_row in english_df.iterrows():
        try:
            lex_key = int(eng_row["keyLexeme"])  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if lex_key not in first_meaning:
            val = str(eng_row["strMeaning"])
            first_meaning[lex_key] = "" if val == "nan" else val.strip()

    db.execute(
        """
        CREATE TABLE sedra (
            lexeme  TEXT NOT NULL,
            root    TEXT NOT NULL,
            meaning TEXT NOT NULL
        )
        """
    )

    rows: list[tuple[str, str, str]] = []
    for raw_key, lex_row in lexemes_df.iterrows():
        try:
            key_lex = int(raw_key)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        lexeme = _translit(str(lex_row["strLexeme"]))

        root = ""
        try:
            key_root = int(lex_row["keyRoot"])  # type: ignore[arg-type]
            if key_root in roots_df.index:
                root = _translit(str(roots_df.loc[key_root, "strRoot"]))
        except (TypeError, ValueError):
            pass

        rows.append((lexeme, root, first_meaning.get(key_lex, "")))

    db.executemany(
        "INSERT INTO sedra (lexeme, root, meaning) VALUES (?, ?, ?)",
        rows,
    )
    db.commit()
    logger.info("Inserted %d SEDRA lexicon entries", len(rows))
