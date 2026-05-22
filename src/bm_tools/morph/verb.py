"""Parse Verbs."""

from dataclasses import dataclass

from bm_tools.morph.constants import (
    HEB_DAGESH,
    HEB_HATAF_PATAH,
    HEB_HATAF_QAMATS,
    HEB_HATAF_SEGOL,
    HEB_HIRIQ,
    HEB_HOLAM,
    HEB_PATAH,
    HEB_QAMATS,
    HEB_QUBUTS,
    HEB_SEGOL,
    HEB_SHEVA,
    HEB_SHIN_DOT,
    HEB_SIN_DOT,
    HEB_TSERE,
)
from bm_tools.morph.helpers import constanants, is_consanant
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebVerb",
    "is_verb",
)

# Qal perfect suffixes: (suffix_string, person, gender, number)
# Ordered longest-first to prevent partial matches.
# In the UXLC text encoding, the vowel appears BEFORE the dagesh on ת.
_PERF_SUFFIXES: tuple[tuple[str, str, str, str], ...] = (
    (HEB_SHEVA + "ת" + HEB_HIRIQ + HEB_DAGESH + "י", "1", "c", "s"),  # תִּי  1cs
    (HEB_SHEVA + "ת" + HEB_SEGOL + HEB_DAGESH + "ם", "2", "m", "p"),  # תֶּם  2mp
    (HEB_SHEVA + "ת" + HEB_SEGOL + HEB_DAGESH + "ן", "2", "f", "p"),  # תֶּן  2fp
    (HEB_SHEVA + "ת" + HEB_QAMATS + HEB_DAGESH, "2", "m", "s"),  # תָּ   2ms
    (HEB_SHEVA + "ת" + HEB_SHEVA + HEB_DAGESH, "2", "f", "s"),  # תְּ   2fs
    (HEB_SHEVA + "נ" + "ו" + HEB_DAGESH, "1", "c", "p"),  # נוּ  1cp
    ("ו" + HEB_DAGESH, "3", "c", "p"),  # וּ   3cp
    (HEB_QAMATS + "ה", "3", "f", "s"),  # ָה   3fs
)

# Allowed theme vowels under C₂ for Qal perfect 3ms identification.
# Patah: standard a-class verbs (שָׁמַר).
# Tsere: stative e-class verbs (כָּבֵד).
# Qamats on C₂ is excluded to avoid nouns like אָמָה (maidservant).
_QAL_PERF_3MS_C2_VOWELS = (HEB_PATAH, HEB_TSERE)

# Imperfect (yiqtol) tables.

# Preformative consonants for all imperfect forms.
_IMPF_PREFORMATIVES = ("י", "ת", "א", "נ")

# Valid vowels on the preformative consonant across all imperfect stems.
# Hiriq: standard Qal/Niphal/Hiphil (יִ, תִ, נִ).
# Holem: pe-aleph Qal (יֹ) where aleph quiesces.
# Segol: 1cs Qal (אֶ).
# Tsere: Niphal (יֵ).
# Patah: Hiphil (יַ).
# Sheva: Piel/Pual/Hithpael (יְ); reduced vowel on preformative before intensive stem.
# Hataf forms: before guttural preformatives.
_IMPF_PREFORMATIVE_VOWELS = (
    HEB_HIRIQ,
    HEB_HOLAM,
    HEB_SEGOL,
    HEB_TSERE,
    HEB_PATAH,
    HEB_SHEVA,
    HEB_HATAF_PATAH,
    HEB_HATAF_SEGOL,
    HEB_HATAF_QAMATS,
)

# Theme vowels on C₂ (consonant index 2) expected in bare imperfect forms.
# Qamats included: aleph-final roots (קרא, ירא) lengthen to qamats before quiescent aleph.  # noqa: E501
_IMPF_THEME_VOWELS = (HEB_HOLAM, HEB_PATAH, HEB_TSERE, HEB_SEGOL, HEB_QAMATS)

# Imperfect suffixes: (suffix, person, gender, number, required_preformative).
# Ordered longest-first. The required_preformative disambiguates tav forms.
_IMPF_SUFFIXES: tuple[tuple[str, str, str, str, str], ...] = (
    ("נ" + HEB_QAMATS + "ה", "3", "f", "p", "י"),  # נָה + yod  → 3fp
    ("נ" + HEB_QAMATS + "ה", "2", "f", "p", "ת"),  # נָה + tav  → 2fp
    (HEB_HIRIQ + "י", "2", "f", "s", "ת"),  # ִי  + tav  → 2fs
    ("ו" + HEB_DAGESH, "3", "m", "p", "י"),  # וּ  + yod  → 3mp
    ("ו" + HEB_DAGESH, "2", "m", "p", "ת"),  # וּ  + tav  → 2mp
)

# Bare imperfect (no suffix): (preformative, person, gender, number).
# Tav is ambiguous (2ms or 3fs); defaulting to 2ms.
_IMPF_BARE: tuple[tuple[str, str, str, str], ...] = (
    ("י", "3", "m", "s"),
    ("ת", "2", "m", "s"),
    ("א", "1", "c", "s"),
    ("נ", "1", "c", "p"),
)

_SKIP_DIACRITICS = (HEB_DAGESH, HEB_SHIN_DOT, HEB_SIN_DOT)
_HATAF_VOWELS = (HEB_HATAF_PATAH, HEB_HATAF_SEGOL, HEB_HATAF_QAMATS)
# 3-consonant imperfect allows qamats and qubuts preformatives
# (qamats: יָּשֶׁב, יָבִא; qubuts: Hophal יֻתַּן)
# in addition to the standard imperfect preformative vowels.
_3CONS_IMPF_PREFORMATIVE_VOWELS = (*_IMPF_PREFORMATIVE_VOWELS, HEB_QAMATS, HEB_QUBUTS)


@dataclass(frozen=True)
class HebVerb:
    """Hebrew Verb."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None
    person: str  # 1, 2, 3
    gender: str  # (m)asculin, (f)eminin, (c)ommon
    number: str  # (s)ingular, (p)lural, (d)uel
    tense: str | None
    mood: str | None


def _first_vowel(word: str) -> tuple[str | None, int]:
    """Return (vowel, index) of the vowel under the first consonant.

    Skips dagesh and shin/sin dots which appear between a consonant and its vowel.
    """
    i = 1
    while i < len(word) and word[i] in (HEB_DAGESH, HEB_SHIN_DOT, HEB_SIN_DOT):
        i += 1
    return (word[i] if i < len(word) else None), i


def _is_valid_perf_stem(stem: str) -> bool:
    """Check if stem has exactly 3 consonants with a valid Qal perfect C₁ vowel.

    Qamats under C₁ for 3ms/3fs/2ms/2fs/1cs/3cp/1cp.
    Sheva under C₁ for 2mp/2fp (vowel reduction before heavy suffix).
    """
    if len(constanants(stem)) != 3:  # noqa: PLR2004
        return False
    vowel, _ = _first_vowel(stem)
    return vowel in (HEB_QAMATS, HEB_SHEVA)


def _is_qal_perf_3ms(word: str) -> bool:
    """Check if word matches the Qal Perfect 3ms pattern: CāCaC or CāCēC.

    C₁ must have qamats. C₂ must have patah (a-class) or tsere (stative e-class).
    Excludes C₂ holam/qubuts to avoid conflation with Qal active/passive participles.
    """
    if len(constanants(word)) != 3:  # noqa: PLR2004
        return False
    vowel_c1, i = _first_vowel(word)
    if vowel_c1 != HEB_QAMATS:
        return False
    # Advance past C₁ vowel, skipping any trailing C₁ modifiers (shin/sin dot,
    # dagesh) that the encoding places after the vowel rather than before it.
    i += 1  # past qamats
    while i < len(word) and word[i] in (HEB_DAGESH, HEB_SHIN_DOT, HEB_SIN_DOT):
        i += 1
    # i is now at C₂; skip it and any of its leading modifiers
    if i >= len(word):
        return False
    i += 1  # skip C₂
    while i < len(word) and word[i] in (HEB_DAGESH, HEB_SHIN_DOT, HEB_SIN_DOT):
        i += 1
    if i >= len(word):
        return False
    return word[i] in _QAL_PERF_3MS_C2_VOWELS


def _vowel_at_consonant(word: str, idx: int) -> str | None:
    """Return the vowel diacritic following the idx-th consonant (0-based).

    Skips dagesh and shin/sin-dot which may appear between consonant and vowel.
    """
    count = 0
    i = 0
    while i < len(word):
        if is_consanant(word[i]):
            if count == idx:
                i += 1
                while i < len(word) and word[i] in _SKIP_DIACRITICS:
                    i += 1
                if (
                    i < len(word)
                    and not is_consanant(word[i])
                    and word[i] not in _SKIP_DIACRITICS
                ):
                    return word[i]
                return None
            count += 1
        i += 1
    return None


def _is_valid_impf_stem(word: str) -> bool:
    """Check preformative + 3-consonant root: 4 consonants, valid preformative vowel."""
    if len(constanants(word)) != 4:  # noqa: PLR2004
        return False
    if word[0] not in _IMPF_PREFORMATIVES:
        return False
    vowel, _ = _first_vowel(word)
    return vowel in _IMPF_PREFORMATIVE_VOWELS


def _is_valid_impf_bare(word: str) -> bool:
    """Imperfect bare-form check: stem validity + theme vowel on C₂ (not qamats)."""
    if not _is_valid_impf_stem(word):
        return False
    theme = _vowel_at_consonant(word, 2)
    return theme is None or theme in _IMPF_THEME_VOWELS


def _is_qal_part_ms(word: str) -> bool:
    """Qal active participle ms: C₁(holam)C₂(tsere)C₃, 3 consonants.

    Also catches ayin-he participles: C₁(holam)C₂(segol)ה (e.g. עֹשֶׂה).
    """
    cons = constanants(word)
    if len(cons) != 3:  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_HOLAM:
        return False
    vowel_c2 = _vowel_at_consonant(word, 1)
    if vowel_c2 == HEB_TSERE:
        return True
    # Ayin-he participle: holam + segol + ה-final (e.g. עֹשֶׂה, הֹוֶה)
    return vowel_c2 == HEB_SEGOL and cons[-1] == "ה"


def _is_qal_inf_abs(word: str) -> bool:
    """Qal infinitive absolute: C₁(qamats)C₂(holam)C₃, 3 consonants, not ה-final."""
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] == "ה":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_QAMATS:
        return False
    return _vowel_at_consonant(word, 1) == HEB_HOLAM


def _is_qal_imp(word: str) -> bool:
    """Qal imperative 2ms / infinitive construct: C₁(sheva/hataf)C₂(holam)C₃, 3 consonants.

    Allows ה-final when C₁ has a hataf vowel (ayin-he imperatives, e.g. עֲשֹׂה).
    Excludes ה-final for sheva-C₁ to avoid matching feminine nouns.
    """  # noqa: E501
    cons = constanants(word)
    if len(cons) != 3:  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in (HEB_SHEVA, *_HATAF_VOWELS):
        return False
    if vowel_c1 == HEB_SHEVA and cons[-1] == "ה":
        return False
    return _vowel_at_consonant(word, 1) == HEB_HOLAM


def _is_hataf_c1_verb(word: str) -> bool:
    """Verb with hataf vowel on guttural C₁ (Aramaic Peal perfect or alt Hebrew form).

    Catches אֲמַר, אֱמַר, אֲמָר, אֱמָר. Excludes ה-final to avoid feminine nouns.
    """
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] == "ה":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in _HATAF_VOWELS:
        return False
    return _vowel_at_consonant(word, 1) in (HEB_PATAH, HEB_QAMATS, HEB_TSERE, HEB_SEGOL)


def _is_qal_perf_3ms_qamats_c2(word: str) -> bool:
    """Qal perfect 3ms with qamats on both C₁ and C₂, 3 consonants, not ה-final.

    Catches נָתָן (he gave) and אָמָר where the UXLC text has qamats on C₂
    instead of the expected patah.  Excludes ה-final to avoid feminine nouns.
    """
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] == "ה":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_QAMATS:
        return False
    return _vowel_at_consonant(word, 1) == HEB_QAMATS


def _is_niphal_perf(word: str) -> bool:
    """Niphal perfect: C₁(hiriq) + C₂(dagesh) + C₂(patah/qamats/tsere) + C₃, 3 consonants.

    Pattern: nִXXX where the hiriq on C₁ signals Niphal.
    Catches נִתַּן (he was given), נִתָּן, נִשְׁמַר, etc.
    """  # noqa: E501
    if len(constanants(word)) != 3:  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_HIRIQ:
        return False
    # C₂ must have dagesh forte (Niphal doubling)
    vowel_c2 = _vowel_at_consonant(word, 1)
    return vowel_c2 in (HEB_PATAH, HEB_QAMATS, HEB_TSERE, HEB_SEGOL)


def _is_pe_aleph_quiescent_inf(word: str) -> bool:
    """Pe-aleph inf construct with quiescent aleph: א + (no vowel) + C₂(holam) + C₃.

    Catches אמֹר (stripped from לֵאמֹר) where aleph has no vowel diacritic.
    """
    if len(constanants(word)) != 3 or word[0] != "א":  # noqa: PLR2004
        return False
    # Aleph is quiescent when the next character is a consonant (no intervening vowel)
    if len(word) < 2 or not is_consanant(word[1]):  # noqa: PLR2004
        return False
    return _vowel_at_consonant(word, 1) == HEB_HOLAM


def _is_ayin_he_qal(word: str) -> bool:
    """Qal forms of ayin-he roots: 3 consonants with ה final, qamats or hataf on C₁.

    Catches:
    - Perfect 3ms: C₁(qamats) + C₂(qamats) + ה  (e.g. הָיָה, בָּנָה)
    - Inf absolute: C₁(qamats) + C₂(holam) + ה  (e.g. הָיֹה)
    - Imperative / inf construct: C₁(hataf) + C₂(tsere) + ה  (e.g. הֱיֵה)
    """
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] != "ה":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    vowel_c2 = _vowel_at_consonant(word, 1)
    if vowel_c1 == HEB_QAMATS and vowel_c2 in (HEB_QAMATS, HEB_HOLAM):
        return True
    # Imperative / inf construct: C₁(hataf) + C₂(tsere/qamats) + ה (e.g. הֱיֵה, עֲשָׂה)
    if vowel_c1 in _HATAF_VOWELS and vowel_c2 in (HEB_TSERE, HEB_QAMATS):
        return True
    # Fs participle / other: C₁(holam) + C₂(qamats) + ה (e.g. עֹשָׂה)
    return bool(vowel_c1 == HEB_HOLAM and vowel_c2 == HEB_QAMATS)


def _is_pe_aleph_impf_1cs(word: str) -> bool:
    """Pe-aleph Qal imperfect 1cs: aleph(holam)C₂(patah)C₃, 3 consonants.

    Catches אֹמַר (I will say) where the preformative and root aleph merge.
    """
    if len(constanants(word)) != 3 or word[0] != "א":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_HOLAM:
        return False
    return _vowel_at_consonant(word, 1) == HEB_PATAH


def _is_3cons_impf(word: str) -> bool:
    """3-consonant imperfect (pe-yod/pe-nun weak verbs and Hiphil of weak roots).

    Catches imperfect forms where the first root consonant drops or assimilates,
    leaving only 3 consonants: preformative + 2 root consonants.
    Examples: יֵשֶׁב (pe-yod Qal), יַשֵּׁב (Hiphil), יִּשְׁבְּ (truncated),
              יָבִא (pe-aleph/pe-yod of בוא), יֹּשֶׁב (pe-yod participle variant).
    Excludes ה-final (handled by _is_ayin_he_qal).
    """
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] == "ה":  # noqa: PLR2004
        return False
    if word[0] not in _IMPF_PREFORMATIVES:
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in _3CONS_IMPF_PREFORMATIVE_VOWELS:
        return False
    return _vowel_at_consonant(word, 1) is not None


def is_verb(elements: CommonElements) -> HebVerb | None:  # noqa: PLR0912, C901, PLR0911
    """Is the word a Verb?"""
    word = elements.word

    # Try each perfect suffix (longest first to avoid partial matches)
    for suffix, person, gender, number in _PERF_SUFFIXES:
        if word.endswith(suffix) and _is_valid_perf_stem(word[: -len(suffix)]):
            return HebVerb(
                definite_article=elements.definite_article,
                gender=gender,
                mood=None,
                number=number,
                person=person,
                preposition=elements.preposition,
                raw=elements.raw,
                tense="perfect",
                vav_consec=elements.vav_consec,
                word=word,
                word_constanants=constanants(word),
            )

    # Try 3ms: no suffix, CāCaC / CāCēC vowel pattern
    if _is_qal_perf_3ms(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="perfect",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Try imperfect suffixed forms (longest suffix first)
    for suffix, person, gender, number, expected_preformative in _IMPF_SUFFIXES:
        if word.endswith(suffix):
            stem = word[: -len(suffix)]
            if _is_valid_impf_stem(stem) and stem[0] == expected_preformative:
                return HebVerb(
                    definite_article=elements.definite_article,
                    gender=gender,
                    mood=None,
                    number=number,
                    person=person,
                    preposition=elements.preposition,
                    raw=elements.raw,
                    tense="imperfect",
                    vav_consec=elements.vav_consec,
                    word=word,
                    word_constanants=constanants(word),
                )

    # Try bare imperfect forms (3ms, 2ms/3fs, 1cs, 1cp)
    if _is_valid_impf_bare(word):
        for preformative, person, gender, number in _IMPF_BARE:
            if word[0] == preformative:
                return HebVerb(
                    definite_article=elements.definite_article,
                    gender=gender,
                    mood=None,
                    number=number,
                    person=person,
                    preposition=elements.preposition,
                    raw=elements.raw,
                    tense="imperfect",
                    vav_consec=elements.vav_consec,
                    word=word,
                    word_constanants=constanants(word),
                )

    # Qal perfect 3ms with qamats on both C₁ and C₂ (e.g. נָתָן, אָמָר)
    if _is_qal_perf_3ms_qamats_c2(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="perfect",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Niphal perfect: C₁(hiriq) + C₂(patah/qamats/tsere) (e.g. נִתַּן, נִתָּן)
    if _is_niphal_perf(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="perfect",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Pe-aleph inf construct with quiescent aleph (e.g. אמֹר stripped from לֵאמֹר)
    if _is_pe_aleph_quiescent_inf(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood="imperative",
            number="s",
            person="2",
            preposition=elements.preposition,
            raw=elements.raw,
            tense=None,
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Ayin-he Qal forms (ה-final roots): הָיָה, בָּנָה, הָיֹה, הֱיֵה
    if _is_ayin_he_qal(word):
        vowel_c1, _ = _first_vowel(word)
        vowel_c2 = _vowel_at_consonant(word, 1)
        if vowel_c1 in _HATAF_VOWELS:
            tense, mood, person, gender, number = None, "imperative", "2", "m", "s"
        elif vowel_c2 == HEB_HOLAM:
            tense, mood, person, gender, number = "infinitive", "absolute", "", "", ""
        else:
            tense, mood, person, gender, number = "perfect", None, "3", "m", "s"
        return HebVerb(
            definite_article=elements.definite_article,
            gender=gender,
            mood=mood,
            number=number,
            person=person,
            preposition=elements.preposition,
            raw=elements.raw,
            tense=tense,
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Qal active participle ms: C₁(holam)C₂(tsere)
    if _is_qal_part_ms(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Qal infinitive absolute: C₁(qamats)C₂(holam)
    if _is_qal_inf_abs(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="",
            mood="absolute",
            number="",
            person="",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="infinitive",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Qal imperative 2ms / infinitive construct: C₁(sheva/hataf)C₂(holam)
    if _is_qal_imp(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood="imperative",
            number="s",
            person="2",
            preposition=elements.preposition,
            raw=elements.raw,
            tense=None,
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Verb with hataf on guttural C₁ (Aramaic Peal perfect, alt Hebrew forms)
    if _is_hataf_c1_verb(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="perfect",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Pe-aleph Qal imperfect 1cs: aleph(holam) + C₂(patah)
    if _is_pe_aleph_impf_1cs(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="c",
            mood=None,
            number="s",
            person="1",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="imperfect",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # 3-consonant imperfect: pe-yod/pe-nun/pe-aleph weak verbs (root cons dropped)
    if _is_3cons_impf(word):
        for preformative, person, gender, number in _IMPF_BARE:
            if word[0] == preformative:
                return HebVerb(
                    definite_article=elements.definite_article,
                    gender=gender,
                    mood=None,
                    number=number,
                    person=person,
                    preposition=elements.preposition,
                    raw=elements.raw,
                    tense="imperfect",
                    vav_consec=elements.vav_consec,
                    word=word,
                    word_constanants=constanants(word),
                )

    return None
