"""Import BDB definitions from Sefaria JSON into haqor.db."""

import json
import re
import sqlite3
from html.parser import HTMLParser
from pathlib import Path

__all__ = ("import_bdb",)

_BDB_FILES = (
    "src_texts/sefaria/sefaria.BDB.json",
    "src_texts/sefaria/sefaria.BDB.Aramaic.json",
)

_NOUN_MARKER = "<strong>n."
_ADJ_MARKER = "<strong>adj."

_LABELED_FORM_RE = re.compile(
    r"(?:pl\.|cstr\.|sf\.|du\.)[^<]{0,20}<span dir=\"rtl\">(.*?)</span>"
)

# ---------------------------------------------------------------------------
# Consonant extraction
# ---------------------------------------------------------------------------


def _consonants(text: str) -> str:
    return "".join(c for c in text if "\u05d0" <= c <= "\u05ea")


# ---------------------------------------------------------------------------
# HTML → Flutter span list parser
# ---------------------------------------------------------------------------


class _SpanBuilder(HTMLParser):
    """Convert a BDB HTML definition string to a list of span dicts.

    Each span dict has at least ``t`` (text).  Optional boolean keys ``b``
    (bold), ``i`` (italic), ``s`` (superscript), ``rtl`` (RTL/Hebrew) and
    string key ``href`` (cross-reference target) are included only when true /
    non-empty to keep JSON compact.
    """

    def __init__(self) -> None:
        super().__init__()
        self._spans: list[dict] = []
        self._style: dict[str, bool] = {
            "b": False,
            "i": False,
            "s": False,
            "rtl": False,
        }
        self._href: str | None = None

    # ------------------------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "strong":
            self._style["b"] = True
        elif tag == "em":
            self._style["i"] = True
        elif tag == "sup":
            self._style["s"] = True
        elif tag == "span":
            if attr.get("dir") == "rtl":
                self._style["rtl"] = True
        elif tag == "a":
            href = attr.get("data-ref") or attr.get("href") or ""
            self._href = href or None

    def handle_endtag(self, tag: str) -> None:
        if tag == "strong":
            self._style["b"] = False
        elif tag == "em":
            self._style["i"] = False
        elif tag == "sup":
            self._style["s"] = False
        elif tag == "span":
            self._style["rtl"] = False
        elif tag == "a":
            self._href = None

    def handle_data(self, data: str) -> None:
        if not data:
            return
        span: dict = {"t": data}
        if self._style["b"]:
            span["b"] = True
        if self._style["i"]:
            span["i"] = True
        if self._style["s"]:
            span["s"] = True
        if self._style["rtl"]:
            span["rtl"] = True
        if self._href:
            span["href"] = self._href
        self._spans.append(span)

    # ------------------------------------------------------------------
    def result(self) -> list[dict]:
        return self._spans


def _parse_definition(html_str: str) -> list[dict]:
    builder = _SpanBuilder()
    builder.feed(html_str)
    return builder.result()


# ---------------------------------------------------------------------------
# Sense tree conversion
# ---------------------------------------------------------------------------


def _convert_sense(sense: dict) -> dict:
    out: dict = {}
    if "num" in sense:
        out["num"] = sense["num"]
    if "pre_num" in sense:
        out["pre_num"] = sense["pre_num"]
    if "form" in sense:
        out["form"] = sense["form"]
    if "definition" in sense:
        out["definition"] = _parse_definition(sense["definition"])
    if "senses" in sense:
        out["senses"] = [_convert_sense(s) for s in sense["senses"]]
    return out


def _content_to_json(content: dict) -> str:
    senses = [_convert_sense(s) for s in content.get("senses", [])]
    return json.dumps({"senses": senses}, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Gloss extraction
# ---------------------------------------------------------------------------

# Matches a POS prefix at the start of a gloss string.
# Only strips known grammatical abbreviations so that actual gloss words
# like "coll." are left intact.
# Covers: n  m  f  pr  vb  adj  adv  prep  conj  interj  pron  num
#         gent  loc  div  denom  verbal  abs  cstr  sf
_POS_COMPONENT = r"(?:n|m|f|pr|vb|adj|adv|prep|conj|interj|pron|num|gent|loc|div|denom|verbal|abs|cstr|sf)"  # noqa: E501
_POS_RE = re.compile(rf"^(?:{_POS_COMPONENT}\.\s*)+")


def _strip_pos(text: str) -> str:
    """Remove a leading POS abbreviation block and trailing etymology opener."""
    text = _POS_RE.sub("", text).strip()
    if text.endswith("("):
        text = text[:-1].strip()
    return text


_CROSS_REF_PREFIXES = {"v.", "v", "cf.", "cf", "see"}
# Non-gloss values that can survive POS stripping
_NON_GLOSS = {"id.", "id", "coll."}
_PROPER_NAME_RE = re.compile(r"^n\.(?:pr\.|gent\.)")
_PUNCT_RE = re.compile(r"^[\W\d]+$")  # only punctuation / digits


def _clean_gloss(text: str) -> str:
    """Return *text* if it looks like a real gloss, else empty string."""
    text = text.strip(" .,;:")
    if not text or len(text) < 2 or text in _NON_GLOSS:  # noqa: PLR2004
        return ""
    if _PUNCT_RE.match(text):
        return ""
    return text


def _extract_gloss(senses: list[dict]) -> str:
    """Extract a short meaning gloss from the first definition's bold text.

    Strips the POS prefix (n.m., vb., adj.gent., etc.) leaving only the
    actual meaning.  For proper-name entries (n.pr.*, adj.gent.) the meaning
    is often in italic spans rather than bold, so those are tried as a fallback.
    """
    for sense in senses:
        defn = sense.get("definition", "")
        if not defn:
            continue
        spans = _parse_definition(defn)

        # Cross-references ("v. אבדון") have no gloss — skip entirely.
        first_text = spans[0]["t"].strip() if spans else ""
        if first_text in _CROSS_REF_PREFIXES:
            return ""

        bold_parts = [s["t"] for s in spans if s.get("b")]
        raw_bold = " ".join(
            p.strip("( )") for p in bold_parts if p.strip("( )")
        ).strip()
        gloss = _clean_gloss(_strip_pos(raw_bold))
        if gloss:
            return gloss

        # For proper names, the meaning is in italic spans (e.g. "my father is joy").
        # Only use italic for proper-name entries — for root/verb entries italic text
        # is Akkadian/Arabic cognates, not Hebrew meaning.
        if not _PROPER_NAME_RE.match(raw_bold):
            continue

        italic_parts: list[str] = []
        for span in spans:
            if not span.get("i") or span.get("href"):
                continue
            text = span["t"].strip()
            if ";" in text:
                italic_parts.append(text[: text.index(";")].strip())
                break
            italic_parts.append(text)
        italic = _clean_gloss(" ".join(italic_parts))
        if italic:
            return italic

    return ""


# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS bdb (
    headword     TEXT PRIMARY KEY,
    consonants   TEXT NOT NULL,
    gloss        TEXT NOT NULL,
    content_json TEXT NOT NULL
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS bdb_consonants ON bdb (consonants);
"""

_INSERT = """
INSERT OR REPLACE INTO bdb (headword, consonants, gloss, content_json)
VALUES (?, ?, ?, ?);
"""


# ---------------------------------------------------------------------------
# Noun/adjective consonant extraction
# ---------------------------------------------------------------------------


def _extract_noun_consonants(data: list[dict]) -> set[str]:
    """Extract noun/adjective consonant lemmas from raw BDB JSON entries.

    Mirrors the logic previously in ``data_gen.gen_noun_lemmas``: filters
    for entries whose first definition contains a noun or adjective marker,
    then collects consonants for the headword and any explicitly labelled
    inflected forms (pl./cstr./sf./du.) found in the post-etymology section.
    """
    lemmas: set[str] = set()
    for entry in data:
        hw: str = entry["headword"]
        senses = entry.get("content", {}).get("senses", [])
        if not senses:
            continue
        first = senses[0]
        if "definition" not in first:
            continue
        defn: str = first["definition"]
        if _NOUN_MARKER not in defn and _ADJ_MARKER not in defn:
            continue
        c = _consonants(hw)
        if c:
            lemmas.add(c)
        dash_idx = defn.find("—")
        if dash_idx < 0:
            dash_idx = defn.find("—")
        sections: list[str] = []
        if dash_idx >= 0:
            sections.append(defn[dash_idx:])
            paren_idx = defn.find("(", 0)
            if 0 < paren_idx < dash_idx:
                sections.append(defn[:paren_idx])
        else:
            sections.append(defn)
        for section in sections:
            for match in _LABELED_FORM_RE.finditer(section):
                form = match.group(1)
                if " " in form:
                    continue
                c2 = _consonants(form)
                if len(c2) >= 2:  # noqa: PLR2004
                    lemmas.add(c2)
    return lemmas


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def import_bdb(*, src_root: Path, db_path: Path) -> int:
    """Import BDB definitions from Sefaria JSON into *db_path*.

    Processes both the Hebrew and Aramaic BDB JSON files.  Populates:
    - ``bdb``: full definition cache (headword, consonants, gloss, content_json)
    - ``noun_consonants``: consonant lemmas for noun/adjective entries only,
      used by the morphology parser to avoid misclassifying nouns as verbs.

    Returns the number of rows inserted into ``bdb``.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(_CREATE_TABLE)
    conn.execute(_CREATE_INDEX)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS noun_consonants (consonants TEXT PRIMARY KEY)"
    )

    total = 0
    noun_cons: set[str] = set()

    for bdb_file in _BDB_FILES:
        json_path = src_root / bdb_file
        if not json_path.exists():
            continue
        data: list[dict] = json.loads(json_path.read_text(encoding="utf-8"))

        rows: list[tuple[str, str, str, str]] = []
        for entry in data:
            headword: str = entry["headword"]
            content: dict = entry.get("content", {})
            senses: list[dict] = content.get("senses", [])

            cons = _consonants(headword)
            gloss = _extract_gloss(senses)
            content_json = _content_to_json(content)

            rows.append((headword, cons, gloss, content_json))

        conn.executemany(_INSERT, rows)
        total += len(rows)
        noun_cons |= _extract_noun_consonants(data)

    conn.executemany(
        "INSERT OR IGNORE INTO noun_consonants VALUES (?)",
        [(c,) for c in noun_cons],
    )
    conn.commit()
    conn.close()

    return total
