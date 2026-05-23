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

_LABELED_FORM_RE = re.compile(
    r"(?:pl\.|cstr\.|sf\.|du\.)[^<]{0,20}<span dir=\"rtl\">(.*?)</span>"
)

# ---------------------------------------------------------------------------
# Consonant extraction
# ---------------------------------------------------------------------------


_HOLAM = "\u05b9"
_HIRIQ = "\u05b4"
_DAGESH = "\u05bc"
_HE = "\u05d4"
_VAV = "\u05d5"
_YOD = "\u05d9"
_NUN_FINAL = "\u05df"
_TAV = "\u05ea"


def _root(text: str) -> str:
    """Extract the trilateral root from a pointed Hebrew headword.

    Uses vowel pointing to distinguish true consonants from matres lectionis:
      - Holam-vav (\u05d5 followed by holam) and shureq (\u05d5 + dagesh) \u2192 strip \u05d5
      - Hiriq-yod (\u05d9 with no own vowel after a hiriq-bearing consonant) \u2192 strip \u05d9
      - Tsere-yod is kept: yod after tsere is usually a root consonant in BDB headwords

    Nominal suffixes are stripped when \u22654 consonants remain:
      \u05d4 (feminine), \u05df (abstract/locative), \u05ea (from -\u016bt abstract suffix)

    Falls back to first 3 consonants as a last resort.
    """
    # Build list of (consonant, diacritics) pairs walking the pointed string.
    cons: list[tuple[str, list[str]]] = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if "\u05d0" <= c <= "\u05ea":
            j = i + 1
            diacs: list[str] = []
            while j < n and not ("\u05d0" <= text[j] <= "\u05ea"):
                diacs.append(text[j])
                j += 1
            cons.append((c, diacs))
            i = j
        else:
            i += 1

    # Filter matres lectionis.
    filtered: list[str] = []
    for idx, (c, diacs) in enumerate(cons):
        if c == _VAV:
            if _HOLAM in diacs:
                continue  # holam-vav: mater for \u00f4
            if _DAGESH in diacs:
                continue  # shureq: mater for \u016b
        elif c == _YOD:
            own_vowel = any("\u05b0" <= d <= "\u05bb" or d == _HOLAM for d in diacs)
            if not own_vowel and idx > 0 and _HIRIQ in cons[idx - 1][1]:
                continue  # hiriq-yod: mater for \u00ee
        filtered.append(c)

    # Strip nominal suffixes only when we still have more than 3 consonants.
    if len(filtered) > 3 and filtered[-1] == _HE:
        filtered.pop()
    if len(filtered) > 3 and filtered[-1] == _NUN_FINAL:
        filtered.pop()
    if len(filtered) > 3 and filtered[-1] == _TAV:
        filtered.pop()

    return "".join(filtered)


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
    root         TEXT NOT NULL,
    pos          TEXT NOT NULL,
    gloss        TEXT NOT NULL,
    content_json TEXT NOT NULL
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS bdb_root ON bdb (root);
"""

_INSERT = """
INSERT OR REPLACE INTO bdb (headword, root, pos, gloss, content_json)
VALUES (?, ?, ?, ?, ?);
"""


# ---------------------------------------------------------------------------
# POS extraction and root collection
# ---------------------------------------------------------------------------


def _extract_pos(senses: list[dict]) -> str:
    """Extract a coarse POS tag from the first BDB definition's bold text."""
    for sense in senses:
        defn = sense.get("definition", "")
        if not defn:
            continue
        spans = _parse_definition(defn)
        bold_parts = [s["t"] for s in spans if s.get("b")]
        raw_bold = " ".join(p.strip("( )") for p in bold_parts if p.strip("( )")).strip()
        if not raw_bold:
            continue
        m = _POS_RE.match(raw_bold)
        if not m:
            continue
        pos_str = m.group(0)
        if "vb." in pos_str:
            return "vb"
        if "adj." in pos_str:
            return "adj"
        if "adv." in pos_str:
            return "adv"
        if "prep." in pos_str:
            return "prep"
        if "conj." in pos_str:
            return "conj"
        if "interj." in pos_str:
            return "interj"
        if "pron." in pos_str:
            return "pron"
        if "num." in pos_str:
            return "num"
        if "n." in pos_str:
            return "n"
    return ""


def _extract_all_roots(data: list[dict]) -> list[tuple[str, str]]:
    """Extract (root, pos) pairs for all BDB entries.

    For noun/adjective entries also extracts inflected form consonants
    (pl./cstr./sf./du.) so that variant forms are recognised.
    """
    result: list[tuple[str, str]] = []
    for entry in data:
        hw: str = entry["headword"]
        senses = entry.get("content", {}).get("senses", [])
        if not senses:
            continue
        first = senses[0]
        if "definition" not in first:
            continue
        defn: str = first["definition"]

        pos = _extract_pos(senses)
        if not pos:
            continue

        c = _root(hw)
        if c:
            result.append((c, pos))

        if pos not in ("n", "adj"):
            continue

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
                c2 = _root(form)
                if len(c2) >= 2:  # noqa: PLR2004
                    result.append((c2, pos))
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def import_bdb(*, src_root: Path, db_path: Path) -> int:
    """Import BDB definitions from Sefaria JSON into *db_path*.

    Processes both the Hebrew and Aramaic BDB JSON files.  Populates:
    - ``bdb``: full definition cache (headword, root, pos, gloss, content_json)
    - ``lex_consonants``: (root, pos) pairs for all entries; used by the
      morphology parser for POS disambiguation.

    Returns the number of rows inserted into ``bdb``.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(_CREATE_TABLE)
    conn.execute(_CREATE_INDEX)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS lex_consonants "
        "(root TEXT NOT NULL, pos TEXT NOT NULL, PRIMARY KEY (root, pos))"
    )

    total = 0
    lex_rows: list[tuple[str, str]] = []

    for bdb_file in _BDB_FILES:
        json_path = src_root / bdb_file
        if not json_path.exists():
            continue
        data: list[dict] = json.loads(json_path.read_text(encoding="utf-8"))

        rows: list[tuple[str, str, str, str, str]] = []
        for entry in data:
            headword: str = entry["headword"]
            content: dict = entry.get("content", {})
            senses: list[dict] = content.get("senses", [])

            cons = _root(headword)
            pos = _extract_pos(senses)
            gloss = _extract_gloss(senses)
            content_json = _content_to_json(content)

            rows.append((headword, cons, pos, gloss, content_json))

        conn.executemany(_INSERT, rows)
        total += len(rows)
        lex_rows.extend(_extract_all_roots(data))

    conn.executemany(
        "INSERT OR IGNORE INTO lex_consonants (root, pos) VALUES (?, ?)",
        lex_rows,
    )
    conn.commit()
    conn.close()

    return total
