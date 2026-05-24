"""Create and populate the words_aramaic table in a haqor module DB."""

import sqlite3
from pathlib import Path

from logzero import logger

from bm_tools.sedra.bible import parse_sedra3_bible_db_file
from bm_tools.sedra.db import (
    from_transliteration,
    parse_sedra3_lexemes_db_file,
    parse_sedra3_roots_db_file,
    parse_sedra3_words_db_file,
)

__all__ = ("create_words_aramaic",)

_SEDRA_SRC = Path("src_texts/SEDRA")

_SUFFIX_CONTRACTION = 2

_GENDER = {0: "", 1: "common", 2: "masculine", 3: "feminine"}
_PERSON = {0: "", 1: "third", 2: "second", 3: "first"}
_NUMBER = {0: "", 1: "singular", 2: "plural"}
_STATE = {0: "", 1: "absolute", 2: "construct", 3: "emphatic"}
_TENSE = {
    0: "",
    1: "perfect",
    2: "imperfect",
    3: "imperative",
    4: "infinitive",
    5: "active_participle",
    6: "passive_participle",
    7: "participles",
}
_FORM = {
    0: "",
    1: "peal",
    2: "ethpeal",
    3: "pael",
    4: "ethpael",
    5: "aphel",
    6: "ettaphal",
    7: "shaphel",
    8: "eshtaphal",
    9: "saphel",
    10: "estaphal",
    11: "pauel",
    12: "ethpaual",
    13: "paiel",
    14: "ethpaial",
    15: "palpal",
    16: "ethpalpal",
    17: "palpel",
    18: "ethpalpal2",
    19: "pamel",
    20: "ethpamal",
    21: "parel",
    22: "ethparal",
    23: "pali",
    24: "ethpali",
    27: "pahli",
    28: "ethaphal",
}


def _translit(s: str) -> str:
    if not s:
        return s
    try:
        return from_transliteration(s, alphabet="hebrew")
    except (KeyError, IndexError):
        return s


def _format_suffix(
    suf_gender: int,
    suf_person: int,
    suf_number: int,
    suf_contraction: int,
) -> str:
    if suf_contraction == 0 and suf_gender == 0 and suf_person == 0:
        return ""
    parts = [
        _PERSON.get(suf_person, ""),
        _GENDER.get(suf_gender, ""),
        _NUMBER.get(suf_number, ""),
    ]
    label = "+".join(p for p in parts if p)
    if suf_contraction == _SUFFIX_CONTRACTION:
        label = f"contraction:{label}" if label else "contraction"
    return label


def _count_bfbs_occurrences(src: Path) -> dict[int, int]:
    """Count how many times each tblWords keyWord appears in BFBS.TXT."""
    counts: dict[int, int] = {}
    for _, _, word_id in parse_sedra3_bible_db_file(str(src / "BFBS.TXT")):
        counts[word_id] = counts.get(word_id, 0) + 1
    return counts


def create_words_aramaic(
    db: sqlite3.Connection,
    src: Path = _SEDRA_SRC,
) -> None:
    """Create and populate the ``words_aramaic`` table in *db*.

    Schema mirrors the Hebrew ``words`` table with Aramaic-specific fields:

      raw        TEXT  — vocalized form (strVocalised → Hebrew Unicode)
      word       TEXT  — consonantal form (strWord → Hebrew Unicode)
      root       TEXT  — root consonants (from tblRoots)
      count      INT   — occurrence count in the NT (BFBS)
      enclitic   BOOL  — is this word enclitic
      prefix     INT   — SEDRA3 prefix code (0-63)
      gender     TEXT  — grammatical gender
      person     TEXT  — grammatical person
      number     TEXT  — grammatical number
      state      TEXT  — nominal state (absolute/construct/emphatic)
      tense      TEXT  — verbal tense
      form       TEXT  — verbal conjugation/binyan
      suffix     TEXT  — pronominal suffix description
    """
    words_df = parse_sedra3_words_db_file(str(src / "tblWords.txt"))
    word_counts = _count_bfbs_occurrences(src)

    lexemes_df = parse_sedra3_lexemes_db_file(str(src / "tblLexemes.txt"))
    roots_df = parse_sedra3_roots_db_file(str(src / "tblRoots.txt"))
    roots: dict[int, str] = {}
    for raw_key, lex_row in lexemes_df.iterrows():
        try:
            key_lex = int(raw_key)  # type: ignore[arg-type]
            key_root = int(lex_row["keyRoot"])  # type: ignore[arg-type]
            if key_root in roots_df.index:
                roots[key_lex] = _translit(str(roots_df.loc[key_root, "strRoot"]))
        except (TypeError, ValueError):
            continue

    db.execute(
        """
        CREATE TABLE words_aramaic (
            raw      TEXT,
            word     TEXT,
            root     TEXT,
            count    INT,
            enclitic BOOL,
            prefix     INT,
            gender     TEXT,
            person     TEXT,
            number     TEXT,
            state      TEXT,
            tense      TEXT,
            form       TEXT,
            suffix     TEXT
        )
        """
    )

    rows: list[tuple] = []
    for raw_id, row in words_df.iterrows():
        try:
            word_id = int(raw_id)  # type: ignore[arg-type]
            key_lexeme = int(row["keyLexeme"])  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue

        raw = _translit(str(row["strVocalised"]))
        word = _translit(str(row["strWord"]))

        rows.append(
            (
                raw,
                word,
                roots.get(key_lexeme, ""),
                word_counts.get(word_id, 0),
                bool(row["keyEnclitic"]),
                int(row["keyPrefix"]),  # type: ignore[arg-type]
                _GENDER.get(int(row["keyGender"]), ""),  # type: ignore[arg-type]
                _PERSON.get(int(row["keyPerson"]), ""),  # type: ignore[arg-type]
                _NUMBER.get(int(row["keyNumber"]), ""),  # type: ignore[arg-type]
                _STATE.get(int(row["keyState"]), ""),  # type: ignore[arg-type]
                _TENSE.get(int(row["keyTense"]), ""),  # type: ignore[arg-type]
                _FORM.get(int(row["keyForm"]), ""),  # type: ignore[arg-type]
                _format_suffix(
                    int(row["keySuffixGender"]),  # type: ignore[arg-type]
                    int(row["keySuffixPerson"]),  # type: ignore[arg-type]
                    int(row["keySuffixNumber"]),  # type: ignore[arg-type]
                    int(row["keySuffixContraction"]),  # type: ignore[arg-type]
                ),
            )
        )

    db.executemany(
        """
        INSERT INTO words_aramaic VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        rows,
    )
    db.commit()
    logger.info("Inserted %d words_aramaic entries", len(rows))
