"""Render bible text into different formats."""

from collections.abc import Mapping
from pathlib import Path

from bm_tools.bible import PassageRef
from bm_tools.errors import InvalidOptionError
from bm_tools.render.html import RenderBibleHTML
from bm_tools.render.interface import BibleRenderer, SourceTextReader
from bm_tools.render.md import RenderBibleMarkdown
from bm_tools.render.osis import RenderBibleOSIS
from bm_tools.render.vpl import RenderBibleVPL
from bm_tools.sedra.bible import BFBSSourceTextReader
from bm_tools.uxlc.bible import UXLCSourceTextReader

__all__ = ("render_bible",)

_BIBLE_RENDERERS: Mapping[str, BibleRenderer] = {
    "txt": RenderBibleVPL,
    "vpl": RenderBibleVPL,
    "md": RenderBibleMarkdown,
    "html": RenderBibleHTML,
    "osis": RenderBibleOSIS,
}

_BIBLE_SRC_TEXT: Mapping[str, SourceTextReader] = {
    "bfbs": BFBSSourceTextReader,  # sedra 3 bible text BFBS
    "uxlc": UXLCSourceTextReader,  # Unicode XML Leningrad Codex (WLC)
}


def _get_source_reader(source: str) -> SourceTextReader:
    """Get a source text reader."""
    if source not in _BIBLE_SRC_TEXT:
        raise InvalidOptionError("SourceTextReader", _BIBLE_SRC_TEXT, source)

    return _BIBLE_SRC_TEXT[source]


def _get_bible_renderer(fmt: str, output_path: Path) -> BibleRenderer:
    """Get bible renderer."""
    if fmt not in _BIBLE_RENDERERS:
        raise InvalidOptionError("BibleRenderer", _BIBLE_RENDERERS, fmt)

    return _BIBLE_RENDERERS[fmt](
        output_path=output_path,
    )


def notify_state_changed(
    renderer: BibleRenderer,
    ref_old: PassageRef,
    ref_new: PassageRef,
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


def render_all(output_path: Path) -> None:
    """Render all the supported modules."""
    for source in ("bfbs", "uxlc"):
        for fmt in ("vpl", "md", "html", "osis"):
            for alphabet in ("hebrew", "syriac"):
                render_bible(
                    alphabet=alphabet,
                    source=source,
                    fmt=fmt,
                    output_path=output_path,
                )


def render_bible(
    source: str,
    fmt: str,
    alphabet: str,
    output_path: Path,
) -> None:
    """Render a bible module from the source text in the given format.

    Args:
        source: the module source text
        fmt: module format
        alphabet: alphabet to use for the bible text
        output_path: path to output the module to
    """
    source_reader = _get_source_reader(
        source=source,
    )

    if not source_reader.supports_alphabet(alphabet=alphabet):
        return

    output_path.mkdir(parents=True, exist_ok=True)
    renderer = _get_bible_renderer(
        fmt=fmt,
        output_path=output_path,
    )

    current_ref: PassageRef | None = None

    mod_name = f"{source}_{alphabet}"
    renderer.start_mod(name=mod_name)

    try:
        for ref, words in source_reader.readlines():
            if ref != current_ref:
                if current_ref is None:
                    renderer.start_book(ref.book)
                    renderer.start_chapter(ref.chapter)
                    renderer.start_verse(ref.verse)
                else:
                    notify_state_changed(renderer, ref_old=current_ref, ref_new=ref)

                current_ref = ref

            for word in words:
                renderer.add_word(word)

        renderer.end_verse()
        renderer.end_chapter()
        renderer.end_book()

    finally:
        renderer.end_mod()
