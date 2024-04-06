"""Render bible text into different formats
"""

from typing import Mapping, Type

from .interface import BibleRenderer
from .txt import RenderBibleText

__all__ = ("get_bible_renderer",)

_BIBLE_RENDERERS: Mapping[str, Type[BibleRenderer]] = {
    "txt": RenderBibleText,
}


def get_bible_renderer(name: str, **kwargs) -> BibleRenderer:
    """Get a BibleRenderer to render a bible"""
    if name not in _BIBLE_RENDERERS:
        renderers = list(_BIBLE_RENDERERS.keys())
        raise KeyError(
            f"BibleRenderer '{name}' is not defined, " f"must be one of {renderers}"
        )

    return _BIBLE_RENDERERS[name](**kwargs)
