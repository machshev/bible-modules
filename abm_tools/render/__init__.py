"""Render bible text into different formats
"""

import sys
from typing import Callable, List, Mapping, Optional

from abm_tools.sedra.bible import SEDRAPassageRef, parse_sedra3_bible_db_file
from abm_tools.sedra.db import from_transliteration, parse_sedra3_words_db_file

from .html import RenderBibleHTML
from .interface import BibleRenderer
from .txt import RenderBibleText

__all__ = ("get_bible_renderer",)

_BIBLE_RENDERERS: List[str] = [
    "txt",
    "md",
    "html",
]


def notify_state_changed(
    renderer: BibleRenderer, ref_old: SEDRAPassageRef, ref_new: SEDRAPassageRef
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


def _generate_module(renderer: BibleRenderer) -> None:
    """Generate the bible module"""

    current_ref: Optional[SEDRAPassageRef] = None

    renderer.start_mod()

    for ref, _, word_id in parse_sedra3_bible_db_file():
        if ref != current_ref:
            if current_ref is None:
                renderer.start_book(ref.book)
                renderer.start_chapter(ref.chapter)
                renderer.start_verse(ref.verse)
            else:
                notify_state_changed(renderer, ref_old=current_ref, ref_new=ref)

            current_ref = ref

        renderer.add_word(word_id)

    renderer.end_verse()
    renderer.end_chapter()
    renderer.end_book()
    renderer.end_mod()


def get_bible_renderer(fmt: str, alphabet: str) -> Callable:
    """Get a BibleRenderer to render a bible"""
    if fmt not in _BIBLE_RENDERERS:
        raise KeyError(
            f"BibleRenderer '{fmt}' is not defined, "
            f"must be one of {_BIBLE_RENDERERS}"
        )

    renderer: Optional[BibleRenderer] = None

    if fmt in ["txt", "md"]:
        renderer = RenderBibleText(
            stream=sys.stdout,
            transliterator=lambda w: from_transliteration(w, alphabet=alphabet),
        )

    elif fmt == "html":
        renderer = RenderBibleHTML(
            stream=sys.stdout,
            transliterator=lambda w: from_transliteration(w, alphabet=alphabet),
        )

    if renderer is None:
        raise TypeError("Format type not handled")

    def gen_fn():
        _generate_module(
            renderer=renderer,
        )

    return gen_fn
