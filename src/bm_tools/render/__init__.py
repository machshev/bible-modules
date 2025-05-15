"""Render bible text into different formats."""

from pathlib import Path

from bm_tools.errors import InvalidOptionError
from bm_tools.render.haqor import RenderBibleHaqor
from bm_tools.render.html import RenderBibleHTML
from bm_tools.render.interface import BibleRenderer
from bm_tools.render.md import RenderBibleMarkdown
from bm_tools.render.osis import RenderBibleOSIS
from bm_tools.render.vpl import RenderBibleVPL
from bm_tools.sedra.bible import SEDRAPassageRef, parse_bible_cache_file

__all__ = ("render_bible",)

_BIBLE_RENDERERS: list[str] = [
    "txt",
    "vpl",
    "md",
    "html",
    "osis",
    "haqor",
]


def _get_bible_renderer(fmt: str, alphabet: str, output_path: Path) -> BibleRenderer:
    """Get bible renderer."""
    if fmt not in _BIBLE_RENDERERS:
        msg = "BibleRenderer"
        raise InvalidOptionError(msg, _BIBLE_RENDERERS, fmt)

    if fmt == "haqor":
        return RenderBibleHaqor(
            output_path=output_path,
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

    msg = "Format type not handled"
    raise TypeError(msg)


def notify_state_changed(
    renderer: BibleRenderer,
    ref_old: SEDRAPassageRef,
    ref_new: SEDRAPassageRef,
) -> None:
    """Update the renderer state with any reference changes."""
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
    """Get a BibleRenderer to render a bible.

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
