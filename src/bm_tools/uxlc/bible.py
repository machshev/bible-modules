"""Module to load UXLC bible text.

The UXLC is a Unicode and XML version of the WLC.
"""

from collections.abc import Iterable
from pathlib import Path

from bm_tools.bible import BibleVerseEntryTuple, PassageRef

__all__ = ("UXLCSourceTextReader",)


class UXLCSourceTextReader:
    """Read the UXLC files."""

    @staticmethod
    def readlines() -> Iterable[BibleVerseEntryTuple]:
        """Get an iterable over all the verses in the UXLC source."""
        words = ["Hello", "This"]
        yield (
            PassageRef(book=0, chapter=1, verse=1),
            words,
        )
