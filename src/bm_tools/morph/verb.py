"""Parse Verbs."""

from dataclasses import dataclass

from bm_tools.morph.constants import (
    HEB_DAGESH,
    HEB_HIRIQ,
    HEB_HOLAM,
    HEB_PATAH,
    HEB_QAMATS,
    HEB_QAMATS_QATAN,
    HEB_SEGOL,
    HEB_SHEVA,
    HEB_TSERE,
)
from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebVerb",
    "is_verb",
)

HEB_SUFFIX = (
    HEB_PATAH + "ה",  # perf.s.3.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_QAMATS,  # perf.s.2.m
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA,  # perf.s.2.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_HIRIQ + "י",  # perf.s.2.f
    "ו" + HEB_DAGESH,  # perf.pl.3.c
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA + "ם",  # perf.s.2.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA + "ן",  # perf.s.2.f
    HEB_SHEVA + "נו" + HEB_DAGESH,  # perf.pl.1.c
    # Nouns
    HEB_HIRIQ + "י",  # to me
    "ו" + HEB_HOLAM,  # to him
    "ך" + HEB_QAMATS_QATAN,  # to you (s.2.m)
    HEB_PATAH + "י",  # my
    HEB_QAMATS + "י",  # my
    HEB_QAMATS_QATAN + "י",  # my
    HEB_TSERE + "י",  # of
    HEB_QAMATS + "ה",  # Her
    HEB_HIRIQ + "ים",  # Pl.m
    "ו" + HEB_HOLAM + "ת",  # Pl.f
    HEB_SEGOL + "ת",  # Pl.f
    HEB_HIRIQ + "ית",  # Pl.f
)

HEB_PREFIX = (
    "י" + HEB_SHEVA,  # y'
    "י" + HEB_HIRIQ,  # Yi
    "י" + HEB_PATAH,  # Ya
    "י" + HEB_QAMATS,  # Ya
    "י" + HEB_QAMATS_QATAN,  # Ya
    "י" + HEB_DAGESH + HEB_SHEVA,  # y'
    "י" + HEB_DAGESH + HEB_HIRIQ,  # Yi
    "י" + HEB_DAGESH + HEB_PATAH,  # Ya
    "ת" + HEB_HIRIQ,  # Ti
    "א" + HEB_SEGOL,  # 'e
)


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


def explode(raw: str) -> tuple[str, str, str]:
    """Separate a word into it's grammatical parts."""
    prefix = ""
    suffix = ""

    for s in HEB_PREFIX:
        if raw.startswith(s):
            prefix = s
            break

    for s in HEB_SUFFIX:
        if raw.endswith(s):
            suffix = s
            break

    # remove prefix/sufix
    word = raw[len(prefix) : len(raw) - len(suffix)]

    return word, prefix, suffix


def is_verb(elements: CommonElements) -> HebVerb | None:
    """Is the word a Verb?"""
    if True:
        return None

    gender = ""
    number = ""
    tense = ""
    mood = ""

    return HebVerb(
        definite_article=elements.definite_article,
        gender=gender,
        mood=mood,
        number=number,
        preposition=elements.preposition,
        raw=elements.raw,
        tense=tense,
        vav_consec=elements.vav_consec,
        word=elements.word,
        word_constanants=constanants(elements.word),
    )
