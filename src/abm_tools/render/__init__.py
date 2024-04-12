"""Render bible text into different formats
"""

import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import List, Optional

from abm_tools.sedra.bible import SEDRAPassageRef, parse_bible_cache_file
from abm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file

from .html import RenderBibleHTML
from .interface import BibleRenderer
from .md import RenderBibleMarkdown
from .osis import RenderBibleOSIS
from .vpl import RenderBibleVPL

__all__ = ("render_bible",)

_BIBLE_RENDERERS: list[str] = [
    "txt",
    "vpl",
    "md",
    "html",
    "osis",
]


def _get_bible_renderer(fmt: str, alphabet: str, output_path: Path) -> BibleRenderer:
    """Get bible renderer"""
    if fmt not in _BIBLE_RENDERERS:
        raise KeyError(
            f"BibleRenderer '{fmt}' is not defined, "
            f"must be one of {_BIBLE_RENDERERS}",
        )

    if fmt in ["txt", "vpl"]:
        return RenderBibleVPL(
            output_path=output_path,
            alphabet=alphabet,
        )

    if fmt == "md":
        return RenderBibleMarkdown(
            output_path=output_path,
            alphabet=alphabet,
        )

    if fmt == "osis":
        return RenderBibleOSIS(
            output_path=output_path,
            alphabet=alphabet,
        )

    if fmt == "html":
        return RenderBibleHTML(
            output_path=output_path,
            alphabet=alphabet,
        )

    raise TypeError("Format type not handled")


def notify_state_changed(
    renderer: BibleRenderer,
    ref_old: SEDRAPassageRef,
    ref_new: SEDRAPassageRef,
):
    """Update the renderer state with any reference changes"""
    if ref_new.verse != ref_old.verse:
        renderer.end_verse()

    if ref_new.chapter != ref_old.chapter:
        renderer.end_chapter()

    if ref_new.book != ref_old.book:
        renderer.end_book()

    if ref_new.book != ref_old.book:
        renderer.start_book(ref_new.book)

    if ref_new.chapter != ref_old.chapter:
        renderer.start_chapter(ref_new.chapter)

    if ref_new.verse != ref_old.verse:
        renderer.start_verse(ref_new.verse)


def render_bible(
    mod_name: str,
    fmt: str,
    alphabet: str,
    output_path: Path,
) -> None:
    """Get a BibleRenderer to render a bible

    Args:
        mod_name: name of the module
        fmt: module format
        alphabet: alphabet to use for the bible text
        output_path: path to output the module to
    """
    output_path.mkdir(parents=True, exist_ok=True)

    renderer = _get_bible_renderer(
        fmt=fmt,
        alphabet=alphabet,
        output_path=output_path,
    )

    current_ref: SEDRAPassageRef | None = None

    renderer.start_mod(name=mod_name)

    try:
        for ref, words in parse_bible_cache_file():
            if ref != current_ref:
                if current_ref is None:
                    renderer.start_book(ref.book)
                    renderer.start_chapter(ref.chapter)
                    renderer.start_verse(ref.verse)
                else:
                    notify_state_changed(renderer, ref_old=current_ref, ref_new=ref)

                current_ref = ref

            for word_id in words:
                renderer.add_word(word_id)

        renderer.end_verse()
        renderer.end_chapter()
        renderer.end_book()

    finally:
        renderer.end_mod()
