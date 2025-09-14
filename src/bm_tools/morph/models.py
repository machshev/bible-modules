"""Data models."""

from dataclasses import dataclass

__all__ = ("HebUnknown",)


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
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel
    prefix: str = ""
    suffix: str = ""
    vav_consec: bool = False
    definite_article: bool = False
    preposition: str | None = None


@dataclass(frozen=True)
class HebPreposition:
    """Hebrew Preposition."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None


@dataclass(frozen=True)
class HebVerb:
    """Hebrew Verb."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel
    tense: str | None
    mood: str | None


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    raw: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel
