"""Morphology parse."""

from bm_tools.morph.adverb import HebAdverb, is_adverb
from bm_tools.morph.article import HebArticle, is_article
from bm_tools.morph.constants import (
    HEB_DAGESH,
    HEB_HATAF_PATAH,
    HEB_HATAF_QAMATS,
    HEB_HATAF_SEGOL,
    HEB_HIRIQ,
    HEB_PATAH,
    HEB_QAMATS,
    HEB_SEGOL,
    HEB_SHEVA,
    HEB_SHIN_DOT,
    HEB_SIN_DOT,
    HEB_TSERE,
    HEBREW_GUTERALS,
    HEBREW_GUTERALS_HARSH,
    HEBREW_GUTERALS_WEAK,
    HEBREW_INSEPARABLE_PREPOSITIONS,
)
from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements, HebUnknown
from bm_tools.morph.noun import HebNoun, is_noun
from bm_tools.morph.preposition import HebPreposition, is_preposition
from bm_tools.morph.pronoun import HebPronoun, is_pronoun
from bm_tools.morph.verb import HebVerb, is_verb
from bm_tools.morph.yahweh import Yahweh, is_yahweh

ParsedWord = (
    Yahweh
    | HebArticle
    | HebPreposition
    | HebPronoun
    | HebAdverb
    | HebNoun
    | HebVerb
    | HebUnknown
)


def parse_vav_consecutive(raw: str) -> tuple[str, bool]:
    """Parse vav consecutive."""
    if raw[0] == "ו" and raw[1] in (
        HEB_SHEVA,
        HEB_PATAH,
        HEB_DAGESH,  # וּ (shureq) = conjunction "and" before ב/כ/מ/פ
        HEB_HIRIQ,  # וִ = conjunction "and" before י (hiriq assimilation)
        HEB_QAMATS,  # וָ = conjunction "and" before ר and some consonants
        HEB_SEGOL,  # וֶ = conjunction "and" before aleph-initial words
        HEB_TSERE,  # וֵ = conjunction "and" (less common variant)
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

    # NFD canonical: vowel appears before dagesh (e.g. לַּ = ל + patah + dagesh).
    # Only applies when the vowel is not sheva (sheva is handled below).
    if raw[1] == HEB_PATAH and raw[3] != HEB_SHEVA and i + 1 < len(raw) and raw[i + 1] == HEB_DAGESH:
        return raw[2 : i + 1] + raw[i + 2 :], True

    # Article before consonant + sheva (no dagesh): e.g. הַלְ, הַנְ, הַמְ
    # These letters resist dagesh forte or have a reduced vowel after the article.
    if raw[1] == HEB_PATAH and raw[3] == HEB_SHEVA:
        return raw[2:], True

    # Fallback: article where dagesh forte is quiesced (e.g. הַשַׁבָּת without dagesh on שׁ).
    # raw[i] should be dagesh but is a vowel instead — strip article without removing any dagesh.
    if raw[1] == HEB_PATAH and i < len(raw) and raw[i] not in (HEB_DAGESH, HEB_SHEVA):
        return raw[2:], True

    return raw, False


def parse_inseparable_prepositions(raw: str) -> tuple[str, str | None, bool]:  # noqa: C901
    """Parse inseparable prepositions."""
    if len(raw) < 5 or raw[0] not in HEBREW_INSEPARABLE_PREPOSITIONS:  # noqa: PLR2004
        return (raw, None, False)

    word = raw
    preposition = None
    definite_article = False

    i = 2 if raw[1] == HEB_DAGESH else 1

    if (raw[0] in ("ב", "כ") and raw[1] in (HEB_DAGESH, HEB_SHEVA, HEB_PATAH, HEB_HIRIQ, HEB_QAMATS, HEB_TSERE)) or (raw[0] == "ל"):
        # TODO: Special cases Yahweh and Elohim

        if raw[i] == HEB_SHEVA:
            # Standard preposition; skip any dagesh forte that follows in DB encoding (e.g. בְּצַ)
            preposition = raw[0]
            j = i + 1
            if j < len(raw) and raw[j] == HEB_DAGESH:
                j += 1
            word = raw[j:]

        elif any(
            [
                # Before Sheva, point with hiriq
                (raw[i] == HEB_HIRIQ and raw[i + 2] == HEB_SHEVA),
                # Before Sheva with shin/sin-dot intervening (e.g. לִשְׁמֹר: ל+hiriq+שׁ(shin-dot)+sheva)
                (raw[i] == HEB_HIRIQ and i + 3 < len(raw) and raw[i + 2] in (HEB_SHIN_DOT, HEB_SIN_DOT) and raw[i + 3] == HEB_SHEVA),
                # Before Composite/hataf Sheva, point with the corresponding short vowel
                (raw[i] == HEB_PATAH and raw[i + 2] == HEB_HATAF_PATAH),
                (raw[i] == HEB_SEGOL and raw[i + 2] == HEB_HATAF_SEGOL),
                (raw[i] == HEB_QAMATS and raw[i + 2] == HEB_HATAF_QAMATS),
                # ל + hataf vowel before Hiphil infinitive or guttural-initial word
                raw[i] in (HEB_HATAF_PATAH, HEB_HATAF_SEGOL, HEB_HATAF_QAMATS),
            ]
        ):
            preposition = raw[0]
            word = raw[i + 1 :]

        # ב/כ + hiriq + dagesh + root (e.g. כִּדְמוּתֵנוּ — before sheva-initial word)
        elif raw[i] == HEB_HIRIQ and i + 1 < len(raw) and raw[i + 1] == HEB_DAGESH:
            preposition = raw[0]
            word = raw[i + 2 :]

        # ב/כ + hiriq + root without dagesh (e.g. בִדְגַת — before sheva-initial word)
        elif raw[i] == HEB_HIRIQ and raw[0] in ("ב", "כ") and i + 1 < len(raw) and raw[i + 1] != "י":
            preposition = raw[0]
            word = raw[i + 1 :]

        # Before Yod Sheva
        elif raw[i] == HEB_HIRIQ and raw[i + 1] == "י":
            preposition = raw[0]
            word = "י" + HEB_SHEVA + raw[i + 2 :]

        # ל + tsere before pe-aleph infinitive construct (e.g. לֵאמֹר)
        # ב/כ + tsere = compensatory lengthening before guttural (e.g. כֵּאלֹהִים)
        elif (raw[0] == "ל" and raw[i] == HEB_TSERE) or (raw[0] == "ל" and raw[i] == HEB_QAMATS) or (raw[0] in ("ב", "כ") and raw[i] == HEB_TSERE):  # noqa: E501
            preposition = raw[0]
            word = raw[i + 1 :]

        # Check for the article
        elif raw[i] in (HEB_PATAH, HEB_SEGOL, HEB_QAMATS):
            candidate, definite_article = parse_definite_article(raw="ה" + raw[i:])
            if definite_article:
                word = candidate
                preposition = raw[0]
            elif i + 1 < len(raw) and raw[i + 1] in HEBREW_GUTERALS:
                # Preposition with compensatory vowel before guttural-initial word
                # (e.g. לָהֶם, בָּהֶם, כָּהֵם — preposition + 3mp/3fp pronoun)
                word = raw[i + 1 :]
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

    for parser in (
        is_yahweh,
        is_article,
        is_preposition,
        is_pronoun,
        is_adverb,
        is_verb,
        is_noun,
    ):
        if parsed := parser(elements=elements):
            return parsed

    # Compound preposition: if a preposition was already stripped but the remaining word
    # starts with another inseparable preposition (e.g. מִלִּפְנֵי → מ + לִפְנֵי → ל + פְנֵי),
    # strip the second preposition and retry.
    if elements.preposition is not None and elements.word:
        word2, prep2, art2 = parse_inseparable_prepositions(raw=elements.word)
        if prep2 is not None and word2 != elements.word:
            compound = CommonElements(
                word=word2,
                raw=raw,
                preposition=elements.preposition,  # keep the outer preposition
                definite_article=elements.definite_article or art2,
                vav_consec=elements.vav_consec,
            )
            for parser in (is_verb, is_noun):
                if parsed := parser(elements=compound):
                    return parsed

    # Interrogative ה (הֲ with hataf-patah): strip ה + hataf-patah prefix and retry.
    # This is unambiguous — patah would overlap with the definite article.
    # E.g. הֲשֹׁמֵר (interrogative "Is he guarding?") → שֹׁמֵר (Qal participle ms).
    if raw[0] == "ה" and len(raw) > 2 and raw[1] == HEB_HATAF_PATAH:  # noqa: PLR2004
        interr_word = raw[2:]
        interr_elements = CommonElements(
            word=interr_word,
            raw=raw,
            preposition=elements.preposition,
            definite_article=elements.definite_article,
            vav_consec=elements.vav_consec,
        )
        for parser in (is_verb, is_noun):
            if parsed := parser(elements=interr_elements):
                return parsed

    # If stripping produced an unrecognised fragment, retry verb/noun on the raw
    # word without any stripping.  This recovers words like בָּרָא where ב is the
    # first root consonant, not a preposition.
    # Require the stripped fragment to have at least 2 consonants to avoid false
    # positives where prep+pronoun (e.g. לָּךְ = ל+ך) is wrongly matched as a verb.
    if elements.word != raw and len(constanants(elements.word)) >= 2:
        bare = CommonElements(
            word=raw,
            raw=raw,
            preposition=None,
            definite_article=False,
            vav_consec=False,
        )
        for parser in (is_verb, is_noun):
            if parsed := parser(elements=bare):
                return parsed

    # If a preposition was stripped but the result was unrecognised, also try the
    # article-only-stripped form (without preposition).  This recovers words like
    # הַלְוִיִּם where ל is the first root consonant of לֵוִי, not the ל preposition.
    if elements.preposition is not None:
        word_art, vav_art = parse_vav_consecutive(raw=raw)
        word_art, art_flag = parse_definite_article(raw=word_art)
        if word_art != elements.word:
            no_prep = CommonElements(
                word=word_art,
                raw=raw,
                preposition=None,
                definite_article=art_flag or elements.definite_article,
                vav_consec=vav_art or elements.vav_consec,
            )
            for parser in (is_noun, is_verb):
                if parsed := parser(elements=no_prep):
                    return parsed

    return HebUnknown(
        word=elements.word,
        word_constanants=constanants(elements.word),
        raw=elements.raw,
        vav_consec=elements.vav_consec,
        definite_article=elements.definite_article,
        preposition=elements.preposition,
    )
