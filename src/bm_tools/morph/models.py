"""Data models."""

from dataclasses import dataclass

__all__ = (
    "CommonElements",
    "HebUnknown",
)


@dataclass(frozen=True)
class CommonElements:
    """The name."""

    raw: str
    word: str
    preposition: str | None
    vav_consec: bool = False
    definite_article: bool = False


@dataclass(frozen=True)
class HebUnknown:
    """Unknown Hebrew word."""

    word: str
    raw: str
    word_constanants: str
    gender: str = ""  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str = ""  # i.e. (s)ingular. (p)lural, and (d)uel
    prefix: str = ""
    suffix: str = ""
    vav_consec: bool = False
    definite_article: bool = False
    preposition: str | None = None
