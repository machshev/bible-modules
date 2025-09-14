"""Morphology parse."""

from bm_tools.morph.article import HebArticle, is_article
from bm_tools.morph.constants import (
    HEB_DAGESH,
    HEB_HATAF_PATAH,
    HEB_HATAF_QAMATS,
    HEB_HATAF_SEGOL,
    HEB_HIRIQ,
    HEB_PATAH,
    HEB_PREFIX,
    HEB_QAMATS,
    HEB_SEGOL,
    HEB_SHEVA,
    HEB_SHIN_DOT,
    HEB_SIN_DOT,
    HEB_SUFFIX,
    HEB_TSERE,
    HEBREW_GUTERALS,
    HEBREW_GUTERALS_HARSH,
    HEBREW_GUTERALS_WEAK,
    HEBREW_INSEPARABLE_PREPOSITIONS,
    HEBREW_PREPOSITIONS,
)
from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import (
    CommonElements,
    HebNoun,
    HebPreposition,
    HebUnknown,
    HebVerb,
)
from bm_tools.morph.yahweh import Yahweh, is_yahweh

ParsedWord = Yahweh | HebArticle | HebPreposition | HebNoun | HebVerb | HebUnknown


def parse_vav_consecutive(raw: str) -> tuple[str, bool]:
    """Parse vav consecutive."""
    if raw[0] == "ו" and raw[1] in (
        HEB_SHEVA,
        HEB_PATAH,
    ):
        return raw[2:], True

    return raw, False


def parse_definite_article(raw: str) -> tuple[str, bool]:
    """Parse the definite article."""
    if len(raw) < 4 or raw[0] != "ה":  # noqa: PLR2004
        return raw, False

    if raw[2] in HEBREW_GUTERALS:
        if any(
            [
                # Segol following Chet Qamats
                (
                    raw[1] == HEB_SEGOL
                    and raw[2] in ("ה", "ע", "ח")
                    and raw[3] == HEB_QAMATS
                ),
                # Qamats following accented Hey or Ayin Qamats
                raw[1] == HEB_QAMATS and raw[2] in ("ה", "ע") and raw[3] == HEB_QAMATS,
                # Weak guteral
                raw[2] in HEBREW_GUTERALS_WEAK and raw[1] == HEB_QAMATS,
                # Strong guteral
                raw[2] in HEBREW_GUTERALS_HARSH and raw[1] == HEB_PATAH,
            ]
        ):
            return raw[2:], True

        return raw, False

    # Normal so expect dargesh
    # Skip shin/sin dot
    i = 4 if raw[3] in (HEB_SHIN_DOT, HEB_SIN_DOT) else 3

    if raw[1] == HEB_PATAH and raw[i] == HEB_DAGESH:
        return raw[2:i] + raw[i + 1 :], True

    return raw, False


def parse_inseparable_prepositions(raw: str) -> tuple[str, str | None, bool]:
    """Parse inseparable prepositions."""
    if len(raw) < 5 or raw[0] not in HEBREW_INSEPARABLE_PREPOSITIONS:  # noqa: PLR2004
        return (raw, None, False)

    word = raw
    preposition = None
    definite_article = False

    i = 2 if raw[1] == HEB_DAGESH else 1

    if (raw[0] in ("ב", "כ") and raw[1] == HEB_DAGESH) or (raw[0] == "ל"):
        # TODO: Special cases Yahweh and Elohim

        if any(
            [
                # Standard preposition
                raw[i] == HEB_SHEVA,
                # Before Sheva, point with hiriq
                (raw[i] == HEB_HIRIQ and raw[i + 2] == HEB_SHEVA),
                # Before Composite/hataf Sheva, point with the corresponding short vowel
                (raw[i] == HEB_PATAH and raw[i + 2] == HEB_HATAF_PATAH),
                (raw[i] == HEB_SEGOL and raw[i + 2] == HEB_HATAF_SEGOL),
                (raw[i] == HEB_QAMATS and raw[i + 2] == HEB_HATAF_QAMATS),
            ]
        ):
            preposition = raw[0]
            word = raw[i + 1 :]

        # Before Yod Sheva
        elif raw[i] == HEB_HIRIQ and raw[i + 1] == "י":
            preposition = raw[0]
            word = "י" + HEB_SHEVA + raw[i + 2 :]

        # Check for the article
        elif raw[i] in (HEB_PATAH, HEB_SEGOL, HEB_QAMATS):
            word, definite_article = parse_definite_article(raw="ה" + raw[i:])
            if definite_article:
                preposition = raw[0]

    elif raw[0] == "מ":
        # Definite article is preserved in full after preposition `Min` and
        # since the article is ה which is guteral, we only check the article
        # here in this path.
        if raw[1] == HEB_TSERE and raw[2] in HEBREW_GUTERALS:
            preposition = raw[0]
            word, definite_article = parse_definite_article(raw=raw[2:])

        elif raw[1] == HEB_HIRIQ and raw[3] == HEB_DAGESH:
            preposition = raw[0]
            word = raw[2] + raw[4:]

    return (word, preposition, definite_article)


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


def common_elements(raw: str) -> CommonElements:
    """Parse common word elements."""
    word, vav_cons = parse_vav_consecutive(raw=raw)
    word, full_definite_article = parse_definite_article(raw=word)
    word, preposition, definite_article = parse_inseparable_prepositions(raw=word)

    return CommonElements(
        word=word,
        raw=raw,
        preposition=preposition,
        vav_consec=vav_cons,
        definite_article=definite_article or full_definite_article,
    )


def morph_eval(raw: str) -> ParsedWord:
    """Evaluate the Morphology of a word."""
    elements = common_elements(raw=raw)

    for parser in (is_yahweh, is_article):
        if parsed := parser(elements=elements):
            return parsed

    word, prefix, suffix = explode(raw=elements.word)
    word_constanants = constanants(word)
    gender = ""
    number = ""
    tense = ""
    mood = ""

    # Known prepositions
    if word in HEBREW_PREPOSITIONS:
        return HebPreposition(
            preposition=elements.preposition,
            vav_consec=elements.vav_consec,
            definite_article=elements.definite_article,
            word=word,
            word_constanants=word_constanants,
            raw=raw,
        )

    if False:  # preposition or definite_article:
        # Add this back in when we can differentiate between verbs and nouns
        return HebVerb(
            preposition=elements.preposition,
            definite_article=elements.definite_article,
            number=number,
            tense=tense,
            mood=mood,
            word=word_constanants,
            raw=raw,
        )

    return HebUnknown(
        word=word,
        word_constanants=word_constanants,
        raw=raw,
        gender=gender,
        number=number,
        vav_consec=elements.vav_consec,
        definite_article=elements.definite_article,
        preposition=elements.preposition,
        prefix=prefix,
        suffix=suffix,
    )
