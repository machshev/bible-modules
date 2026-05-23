"""Parse Verbs."""

import unicodedata
from dataclasses import dataclass

from bm_tools.morph.constants import (
    HEB_DAGESH,
    HEB_HATAF_PATAH,
    HEB_HATAF_QAMATS,
    HEB_HATAF_SEGOL,
    HEB_HIRIQ,
    HEB_HOLAM,
    HEB_HOLAM_HASER,
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
    # Without-sheva variants WITH dagesh: Hiphil/Piel/Niphal non-3ms forms where the
    # preceding stem consonant has a full vowel (patah, hiriq, etc.) instead of sheva.
    # E.g. הֲבֵאתִי (Hiphil 1cs of בוא), הִשְׁבַּתִּי (Hiphil 1cs of שׁבת).
    ("ת" + HEB_HIRIQ + HEB_DAGESH + "י", "1", "c", "s"),  # תִּי  1cs (no sheva before ת)
    ("ת" + HEB_SEGOL + HEB_DAGESH + "ם", "2", "m", "p"),  # תֶּם  2mp (no sheva before ת)
    ("ת" + HEB_SEGOL + HEB_DAGESH + "ן", "2", "f", "p"),  # תֶּן  2fp (no sheva before ת)
    ("ת" + HEB_QAMATS + HEB_DAGESH, "2", "m", "s"),  # תָּ   2ms (no sheva before ת)
    ("ת" + HEB_SHEVA + HEB_DAGESH, "2", "f", "s"),  # תְּ   2fs (no sheva before ת)
    # Lamed-guttural / lamed-aleph variants: ת lacks dagesh (gutturals resist dagesh forte).
    # E.g. מָצָאתִי (1cs of מצא), קָרָאתִי (1cs of קרא), שָׁמַעְתָּ (2ms of שׁמע).
    ("ת" + HEB_HIRIQ + "י", "1", "c", "s"),  # תִי  1cs (no dagesh in ת)
    ("ת" + HEB_SEGOL + "ם", "2", "m", "p"),  # תֶם  2mp (no dagesh in ת)
    ("ת" + HEB_SEGOL + "ן", "2", "f", "p"),  # תֶן  2fp (no dagesh in ת)
    ("ת" + HEB_QAMATS, "2", "m", "s"),  # תָ   2ms (no dagesh in ת)
    ("ת" + HEB_SHEVA, "2", "f", "s"),  # תְ   2fs (no dagesh in ת)
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
# Qamats: hollow/pe-aleph verbs (יָבוֹא, יָּשֶׁב).
# Qubuts: Hophal (יֻתַּן).
# Hataf forms: before guttural preformatives.
_IMPF_PREFORMATIVE_VOWELS = (
    HEB_HIRIQ,
    HEB_HOLAM,
    HEB_SEGOL,
    HEB_TSERE,
    HEB_PATAH,
    HEB_SHEVA,
    HEB_QAMATS,
    HEB_QUBUTS,
    HEB_HATAF_PATAH,
    HEB_HATAF_SEGOL,
    HEB_HATAF_QAMATS,
)

# Theme vowels on C₂ (consonant index 2) expected in bare imperfect forms.
# Qamats: aleph-final roots (קרא, ירא) lengthen to qamats before quiescent aleph.
# Qubuts: Qal imperfect of some roots (e.g. יֵאכֻל from אכל).
_IMPF_THEME_VOWELS = (
    HEB_HOLAM,
    HEB_PATAH,
    HEB_TSERE,
    HEB_SEGOL,
    HEB_QAMATS,
    HEB_QUBUTS,
    HEB_HIRIQ,
    HEB_SHEVA,
    HEB_HATAF_PATAH,
    HEB_HATAF_SEGOL,
    HEB_HATAF_QAMATS,
)

# Imperfect suffixes: (suffix, person, gender, number, required_preformative).
# Ordered longest-first. The required_preformative disambiguates tav forms.
_IMPF_SUFFIXES: tuple[tuple[str, str, str, str, str], ...] = (
    # Energic/paragogic nun with dagesh forte (DB encoding: dagesh before qamats)
    ("נ" + HEB_DAGESH + HEB_QAMATS + "ה", "3", "f", "p", "י"),  # נָּה energic, yod → 3fp
    ("נ" + HEB_DAGESH + HEB_QAMATS + "ה", "2", "f", "p", "ת"),  # נָּה energic, tav → 2fp
    ("נ" + HEB_QAMATS + "ה", "3", "f", "p", "י"),  # נָה + yod  → 3fp
    ("נ" + HEB_QAMATS + "ה", "2", "f", "p", "ת"),  # נָה + tav  → 2fp
    (HEB_HIRIQ + "י", "2", "f", "s", "ת"),  # ִי  + tav  → 2fs
    ("ו" + HEB_DAGESH, "3", "m", "p", "י"),  # וּ  + yod  → 3mp
    ("ו" + HEB_DAGESH, "2", "m", "p", "ת"),  # וּ  + tav  → 2mp
    # Paragogic / energic nun forms
    ("ו" + HEB_DAGESH + "ן", "3", "m", "p", "י"),  # וּן + yod → 3mp + paragogic nun
    ("ו" + HEB_DAGESH + "ן", "2", "m", "p", "ת"),  # וּן + tav → 2mp + paragogic nun
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

from bm_tools.morph.helpers import load_bdb_noun_lemmas

_BDB_NOUN_LEMMAS: frozenset[str] = load_bdb_noun_lemmas()
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


def _nfd_endswith(word: str, suffix: str) -> bool:
    """Endswith with NFD normalization.

    The UXLC database stores dagesh before the vowel on consonants like ת
    (e.g. ת + dagesh + hiriq) while Python string literals use the NFD
    canonical order (ת + hiriq + dagesh, lower CCC first).  Normalising
    both strings to NFD before comparing makes the check encoding-agnostic.
    """
    return unicodedata.normalize("NFD", word).endswith(
        unicodedata.normalize("NFD", suffix)
    )


def _first_vowel(word: str) -> tuple[str | None, int]:
    """Return (vowel, index) of the vowel under the first consonant.

    Skips dagesh and shin/sin dots which appear between a consonant and its vowel.
    """
    i = 1
    while i < len(word) and word[i] in (HEB_DAGESH, HEB_SHIN_DOT, HEB_SIN_DOT):
        i += 1
    return (word[i] if i < len(word) else None), i


def _is_valid_perf_stem(stem: str) -> bool:
    """Check if stem has a valid Qal perfect C₁ vowel.

    Standard: 3 consonants with qamats or sheva under C₁.
    Also allows 2-consonant stems ending in ת for lamed-nun verbs where
    the final nun assimilated into the suffix ת (e.g. נָתַ from נָתַן).
    Also allows 2-consonant stems (any ending) for lamed-he 3cp/3fp where
    the ה of the root drops before the וּ suffix (e.g. בָּכָ from בָּכָה → בָּכוּ).
    Pe-yod: after vav-consecutive strip, the initial י carries no explicit vowel;
    the remaining C₁ (second consonant) must carry a full vowel.
    """
    cons = constanants(stem)
    if len(cons) == 3:  # noqa: PLR2004
        vowel, _ = _first_vowel(stem)
        if vowel in (HEB_QAMATS, HEB_SHEVA):
            return True
        # Pe-yod: yod with no explicit vowel (quiesces after vav-consecutive strip).
        if cons[0] == "י" and (vowel is None or is_consanant(vowel)):
            c1_vowel = _vowel_at_consonant(stem, 1)
            return c1_vowel in (HEB_PATAH, HEB_QAMATS, HEB_HIRIQ, HEB_TSERE, HEB_SHEVA, *_HATAF_VOWELS)
        return False
    if len(cons) == 2:  # noqa: PLR2004
        vowel, _ = _first_vowel(stem)
        return vowel in (HEB_QAMATS, HEB_SHEVA)
    return False


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


def _is_qal_part_fs(word: str) -> bool:
    """Qal active participle fs: C₁(holam)C₂C₃ + ת, 4 consonants.

    Examples: רֹמֶשֶׂת (creeping, fs), עֹשָׂת.
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[-1] != "ת":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    return vowel_c1 == HEB_HOLAM


def _is_qal_imp_plural(word: str) -> bool:
    """Qal imperative 2mp: C₁(sheva/hataf)C₂ + וּ (shureq), 3 consonants.

    Examples: רְדוּ (go down, from ירד), לְכוּ (go, from הלך).
    Handles pe-yod/pe-nun verbs where the first root consonant drops.
    """
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] != "ו":  # noqa: PLR2004
        return False
    if not _nfd_endswith(word, "ו" + HEB_DAGESH):
        return False
    vowel_c1, _ = _first_vowel(word)
    return vowel_c1 in (HEB_SHEVA, *_HATAF_VOWELS)


def _is_qal_inf_abs(word: str) -> bool:
    """Qal infinitive absolute: C₁(qamats)C₂(holam)C₃, 3 consonants, not ה-final.

    Also catches 4-consonant forms with holam-vav mater (e.g. הָלוֹךְ, חָסוֹר).
    """
    cons = constanants(word)
    if cons[-1] == "ה":
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_QAMATS:
        return False
    if len(cons) == 3:  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) == HEB_HOLAM
    # 4-cons with holam-vav mater: C₁(qamats) + C₂ + ו(holam) + C₃ (e.g. הָלוֹךְ, חָסוֹר)
    # Exclude BDB nouns (e.g. שָׁלוֹם) to avoid false positives
    if len(cons) == 4 and cons[2] == "ו" and cons not in _BDB_NOUN_LEMMAS:  # noqa: PLR2004
        return _vowel_at_consonant(word, 2) == HEB_HOLAM
    return False


def _is_qal_imp(word: str) -> bool:
    """Qal imperative 2ms / infinitive construct: C₁(sheva/hataf)C₂(holam/patah/tsere)C₃, 3 cons.

    Allows ה-final when C₁ has a hataf vowel (ayin-he imperatives, e.g. עֲשֹׂה).
    Excludes ה-final for sheva-C₁ to avoid matching feminine nouns.
    Also catches imperatives where C₂ has patah or tsere (e.g. שְׁכַּב, שְׁמַע).
    """  # noqa: E501
    cons = constanants(word)
    if len(cons) != 3:  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in (HEB_SHEVA, *_HATAF_VOWELS):
        return False
    if vowel_c1 == HEB_SHEVA and cons[-1] == "ה":
        return False
    vowel_c2 = _vowel_at_consonant(word, 1)
    if vowel_c2 == HEB_HOLAM:
        return True
    # Allow patah/tsere/segol/qamats on C₂ for imperatives not in BDB noun list
    if vowel_c2 in (HEB_PATAH, HEB_TSERE, HEB_SEGOL, HEB_QAMATS) and cons not in _BDB_NOUN_LEMMAS:
        return True
    # Allow hiriq on C₂ for imperatives not in BDB (e.g. זְעִק, שְׂאִי)
    return bool(vowel_c2 == HEB_HIRIQ and cons not in _BDB_NOUN_LEMMAS)


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
    if len(cons) != 3:  # noqa: PLR2004
        return False
    if word[0] not in _IMPF_PREFORMATIVES:
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in _3CONS_IMPF_PREFORMATIVE_VOWELS:
        return False
    # Theme vowel visible on C₁, OR last cons is ו/י/ה (mater lectionis ending)
    theme = _vowel_at_consonant(word, 1)
    return theme is not None or cons[-1] in ("ו", "י", "ה")


def _is_lamed_he_perf(word: str) -> tuple[str, str, str] | None:
    """Lamed-he Qal perfect where ה→י before consonantal suffixes.

    Patterns:
    - 2ms: C₁C₂יתָ  (4 consonants, patah on final ת, e.g. עָשִׂיתָ)
    - 2fs: C₁C₂ית   (4 consonants, no patah on ת, e.g. עָשִׂית)
    - 1cs: C₁C₂יתִי (5 consonants, e.g. רָאִיתִי, עָשִׂיתִי)
    """  # noqa: RUF002
    cons = constanants(word)
    # 2mp/2fp: 5 consonants ending יתם/יתן
    if len(cons) == 5 and cons[-3] == "י" and cons[-2] == "ת":  # noqa: PLR2004
        vowel_c1, _ = _first_vowel(word)
        if vowel_c1 in (HEB_QAMATS, HEB_HIRIQ, HEB_SHEVA, *_HATAF_VOWELS):
            if cons[-1] == "ם":
                return ("2", "m", "p")
            if cons[-1] == "ן":
                return ("2", "f", "p")

    # 1cs: 5 consonants ending יתי
    if len(cons) == 5 and cons[-3] == "י" and cons[-2] == "ת" and cons[-1] == "י":  # noqa: PLR2004
        vowel_c1, _ = _first_vowel(word)
        if vowel_c1 in (HEB_QAMATS, HEB_HIRIQ, *_HATAF_VOWELS):
            return ("1", "c", "s")
        return None
    # 2ms or 2fs: 4 consonants ending יתָ or ית
    if len(cons) != 4 or cons[-2] != "י" or cons[-1] != "ת":  # noqa: PLR2004
        return None
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in (HEB_QAMATS, HEB_HIRIQ, *_HATAF_VOWELS):
        return None
    # 2ms has patah after final ת; 2fs does not
    word_nfd = unicodedata.normalize("NFD", word)
    if word_nfd.endswith("ת" + HEB_PATAH):
        return ("2", "m", "s")
    return ("2", "f", "s")


def _is_pual_perf(word: str) -> bool:
    """Pual perfect 3ms: C₁(qubuts) + C₂(dagesh forte + vowel) + C₃, 3 consonants.

    Qubuts on C₁ is the diagnostic vowel for Pual (passive of Piel).
    ה-final is allowed because lamed-he roots can appear in Pual (e.g. צֻוָּה).
    Qubuts is distinct from all ayin-he Qal patterns so no conflict exists.
    """
    cons = constanants(word)
    if len(cons) != 3:  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    return vowel_c1 == HEB_QUBUTS


def _has_dagesh_at(word: str, cons_idx: int) -> bool:
    """Return True if the consonant at cons_idx has a dagesh following it."""
    char_idx = 0
    count = 0
    while char_idx < len(word):
        if is_consanant(word[char_idx]):
            if count == cons_idx:
                j = char_idx + 1
                while j < len(word) and not is_consanant(word[j]):
                    if word[j] == HEB_DAGESH:
                        return True
                    j += 1
                return False
            count += 1
        char_idx += 1
    return False


def _is_piel_form(word: str) -> bool:
    """Piel form: C₁(hiriq/tsere/patah/sheva) + C₂(tsere or patah+dagesh) + C₃, 3 consonants.

    Catches Piel perfect 3ms (tsere on C₂) and imperatives (sheva on C₁), and
    the patah-theme pattern (e.g. שִׁלַּח, שִׁלַּם) where dagesh forte on C₂ is diagnostic.
    """
    cons = constanants(word)
    if len(cons) != 3:  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in (HEB_PATAH, HEB_HIRIQ, HEB_TSERE, HEB_QAMATS, HEB_SHEVA, *_HATAF_VOWELS):
        return False
    vowel_c2 = _vowel_at_consonant(word, 1)
    if vowel_c2 == HEB_TSERE:
        return True
    # Patah-theme Piel: C₁(hiriq/sheva) + C₂(dagesh-forte + patah) + C₃
    if vowel_c2 == HEB_PATAH and vowel_c1 in (HEB_HIRIQ, HEB_SHEVA, *_HATAF_VOWELS):
        return _has_dagesh_at(word, 1)
    return False


def _has_shureq(word: str, cons_idx: int) -> bool:
    """Return True if the consonant at cons_idx is ו followed immediately by dagesh (shureq)."""
    char_idx = 0
    count = 0
    while char_idx < len(word):
        if is_consanant(word[char_idx]):
            if count == cons_idx:
                # Found the target consonant; check next char is dagesh
                return (
                    char_idx + 1 < len(word)
                    and word[char_idx] == "ו"
                    and word[char_idx + 1] == HEB_DAGESH
                )
            count += 1
        char_idx += 1
    return False


def _is_ayin_vav_inf(word: str) -> bool:
    """Ayin-vav/ayin-yod infinitive construct or imperative: C₁(no vowel) + C₂(ו/י + holam/shureq) + C₃.

    The DB encodes holam-vav as ו + holam and shureq as ו + dagesh.  C₁ carries no vowel diacritic.
    Catches בוֹא (inf construct/imperative of בוא "to come"), שׁוּב (inf of שׁוב "return") and similar.
    Excludes ה-final and BDB noun lemmas (e.g. קוֹל, שׁוֹר) to avoid false positives.
    """  # noqa: E501, RUF002
    cons = constanants(word)
    if len(cons) != 3 or cons[-1] == "ה":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    if cons[1] not in ("ו", "י"):
        return False
    vowel_c2 = _vowel_at_consonant(word, 1)
    # C₂ (vav/yod) must carry holam (holam-vav) or dagesh (shureq = oo sound)
    if vowel_c2 != HEB_HOLAM and not (vowel_c2 is None and _has_shureq(word, 1)):
        return False
    # C₁ must have no vowel diacritic (only dagesh/shin-dot allowed)
    return _vowel_at_consonant(word, 0) is None


def _is_lamed_nun_perf_1cs(word: str) -> bool:
    """Qal perfect 1cs of lamed-nun verbs (e.g. נָתַתִּי from נָתַן).

    The final nun assimilates to the ת suffix, producing a double-ת pattern.
    Consonant signature: C₁ + C₂(=ת) + ת + י (4 consonants, last 3 are ת-ת-י).
    """  # noqa: RUF002
    cons = constanants(word)
    if len(cons) != 4 or cons[-1] != "י" or cons[-2] != "ת" or cons[-3] != "ת":  # noqa: PLR2004
        return False
    vowel_c1, _ = _first_vowel(word)
    return vowel_c1 in (HEB_QAMATS, HEB_SHEVA)


def _is_hollow_qal(word: str) -> tuple[str | None, str | None, str, str, str] | None:  # noqa: PLR0911
    """Hollow verb (ayin-vav/ayin-yod) 2-consonant Qal forms.

    Qamats on the single consonant = perfect 3ms (e.g. בָּא).
    Holam on the single consonant = imperative/inf construct (e.g. בֹּא).
    Tsere/segol = infinitive construct (e.g. תֵּת from נָתַן, after ל-strip in לָתֶת).
    Excludes roots whose consonants appear in the BDB noun lemma list.
    """
    cons = constanants(word)
    if len(cons) != 2:  # noqa: PLR2004
        return None
    if cons in _BDB_NOUN_LEMMAS:
        return None
    # Mapiq on final ה marks a pronominal suffix (e.g. בָּהּ = "in her"), not a verb root
    if word[-1] == HEB_DAGESH:
        return None
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 == HEB_QAMATS:
        return ("perfect", None, "3", "m", "s")
    # Holam: standard imperative; qubuts: defective shureq imperative (e.g. שֻׁב = שׁוּב)
    if vowel_c1 in (HEB_HOLAM, HEB_QUBUTS):
        return (None, "imperative", "2", "m", "s")
    # Inf construct of assimilated-nun/hollow verbs: tsere or segol on C₁ (e.g. תֵּת, תֶת)
    if vowel_c1 in (HEB_TSERE, HEB_SEGOL):
        return ("infinitive", "construct", "", "", "")
    # Short imperative with patah: pe-lamed dropped (e.g. קַח from לקח, רַד from ירד)
    if vowel_c1 == HEB_PATAH:
        return (None, "imperative", "2", "m", "s")
    return None


def _is_qal_part_ms_holam_vav(word: str) -> bool:
    """Qal active participle ms with holam-vav mater lectionis: 4 consonants.

    Pattern: C₁(no vowel) + ו(holam) + C₂(tsere) + C₃.
    The ו carries the holam (holam-vav), making the consonant count 4.
    Examples: רוֹמֵשׂ (creeping), סוֹבֵב (going around), יוֹשֵׁב (sitting).
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[1] != "ו":  # noqa: PLR2004
        return False
    if _vowel_at_consonant(word, 0) is not None:
        return False
    if _vowel_at_consonant(word, 1) != HEB_HOLAM:
        return False
    return _vowel_at_consonant(word, 2) == HEB_TSERE


def _is_hiphil_perf_3ms(word: str) -> bool:
    """Hiphil perfect 3ms: strong or lamed-he root.

    Standard: ה(hiriq) + C₁(sheva/hataf) + C₂ + יod + C₃, 5 consonants.
    Lamed-he: ה(hiriq) + C₁(sheva/hataf) + C₂ + ה, 4 consonants.
    Examples: הִמְטִיר (he rained), הִשְׁקָה (he watered).
    """
    cons = constanants(word)
    if not cons or cons[0] != "ה":
        return False
    vowel_h, _ = _first_vowel(word)
    # Standard strong: ה(hiriq/segol) + C₁(sheva/hataf) + C₂ + י + C₃, 5 consonants
    # Segol on ה: compensatory vowel before gutturals (e.g. הֶחֱזִיק from חזק)
    if len(cons) == 5 and cons[3] == "י":  # noqa: PLR2004
        if vowel_h not in (HEB_HIRIQ, HEB_SEGOL):
            return False
        return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)
    # Lamed-he: ה(hiriq/segol/patah) + C₁(sheva/hataf) + C₂ + ה, 4 consonants
    # Before gutturals, hiriq lowers to segol or patah (compensatory vowel change)
    if len(cons) == 4 and cons[-1] == "ה":  # noqa: PLR2004
        if vowel_h not in (HEB_HIRIQ, HEB_SEGOL, HEB_PATAH):
            return False
        return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)
    # Pe-nun Hiphil or hollow Hiphil: ה(hiriq/tsere/qamats/holam/hataf) + C₁ + יod + C₃, 4 consonants
    # hiriq: pe-nun (הִגִּיד from נגד, הִשִּׁיא from נשא)
    # tsere: ayin-vav hollow (הֵבִיא from בוא, הֵשִׁיב from שׁוב)
    # qamats: pe-aleph (הָבִיא variant, הָשִׁיב variant)
    # holam: defective form (הֹשִׁיב from ישׁב, defective of הוֹשִׁיב)
    if len(cons) == 4 and cons[2] == "י":  # noqa: PLR2004
        if vowel_h not in (HEB_HIRIQ, HEB_TSERE, HEB_QAMATS, HEB_PATAH, HEB_HOLAM, *_HATAF_VOWELS):
            return False
        return _vowel_at_consonant(word, 1) in (HEB_HIRIQ, HEB_TSERE, HEB_SEGOL, HEB_SHEVA, *_HATAF_VOWELS)
    # 3-consonant hollow Hiphil: ה(tsere/hiriq/segol/qamats/hataf) + C₁(various) + C₂
    # E.g. הֵפַר (Hiphil 3ms of פרר), הֵבֵא (Hiphil 3ms/stem of בוא),
    # הֲקִמֹ- (Hiphil stem of קום before suffix, hataf on ה before non-guttural).
    if len(cons) == 3:  # noqa: PLR2004
        if vowel_h not in (HEB_TSERE, HEB_HIRIQ, HEB_SEGOL, HEB_QAMATS, *_HATAF_VOWELS):
            return False
        c1_vowel = _vowel_at_consonant(word, 1)
        if c1_vowel not in (HEB_PATAH, HEB_SEGOL, HEB_QAMATS, HEB_HIRIQ, HEB_TSERE, HEB_SHEVA, HEB_HOLAM, None):
            return False
        return cons not in _BDB_NOUN_LEMMAS
    return False


def _is_hiphil_part_ms(word: str) -> bool:
    """Hiphil active participle ms: מַ + C₁(sheva/hataf) + C₂ + יod + C₃, 5 consonants."""
    cons = constanants(word)
    if len(cons) != 5 or cons[0] != "מ" or cons[3] != "י":  # noqa: PLR2004
        return False
    vowel_mem, _ = _first_vowel(word)
    if vowel_mem != HEB_PATAH:
        return False
    vowel_c1 = _vowel_at_consonant(word, 1)
    return vowel_c1 in (HEB_SHEVA, *_HATAF_VOWELS)


def _is_hiphil_inf(word: str) -> bool:
    """Hiphil infinitive construct.

    Standard: ה(patah) + C₁(sheva/hataf) + C₂ + יod + C₃, 5 consonants.
    Pe-aleph: ה(qamats) + א(hiriq) + יod + C₃, 4 consonants.
    """
    cons = constanants(word)
    if not cons or cons[0] != "ה":
        return False
    vowel_h, _ = _first_vowel(word)
    if len(cons) == 5 and vowel_h == HEB_PATAH and cons[3] == "י":  # noqa: PLR2004
        vowel_c1 = _vowel_at_consonant(word, 1)
        return vowel_c1 in (HEB_SHEVA, *_HATAF_VOWELS)
    # Lamed-he: ה(patah) + C₁(sheva) + C₂ + ו(holam) + ת (e.g. הַשְׁקוֹת)
    if len(cons) == 5 and vowel_h == HEB_PATAH and cons[3] == "ו" and cons[4] == "ת":  # noqa: PLR2004
        vowel_c1 = _vowel_at_consonant(word, 1)
        return vowel_c1 in (HEB_SHEVA, *_HATAF_VOWELS)
    if len(cons) == 4 and vowel_h == HEB_QAMATS and cons[1] == "א" and cons[2] == "י":  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) == HEB_HIRIQ
    # Lamed-he 4-consonant inf: ה(patah/qamats) + C₁(sheva/hataf) + C₂ + ה (e.g. הַרְבָּה)
    if len(cons) == 4 and cons[-1] == "ה" and vowel_h in (HEB_PATAH, HEB_QAMATS):  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)
    # Lamed-he 5-consonant inf: ה(patah) + C₁(sheva/hataf) + C₂ + C₃ + ה (e.g. הַאְזֵנָּה)
    if len(cons) == 5 and cons[-1] == "ה" and vowel_h in (HEB_PATAH, HEB_QAMATS):  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)
    return False


def _is_piel_part(word: str) -> bool:
    """Piel participle ms (4 cons) or fs (5 cons ending ת): מְ + C₁(patah) + C₂ + C₃[+ת]."""
    cons = constanants(word)
    n = len(cons)
    if n not in (4, 5) or cons[0] != "מ":
        return False
    vowel_mem, _ = _first_vowel(word)
    if vowel_mem != HEB_SHEVA:
        return False
    if n == 5 and cons[-1] != "ת":  # noqa: PLR2004
        return False
    vowel_c1 = _vowel_at_consonant(word, 1)
    return vowel_c1 in (HEB_PATAH, HEB_QAMATS, *_HATAF_VOWELS)


def _is_hollow_hiphil_impf(word: str) -> bool:
    """Hollow Hiphil imperfect: preformative(dagesh) + ו(holam) + C₂ + C₃.

    Catches forms like תּוֹצֵא (Hiphil impf 3fs of יצא).
    """
    cons = constanants(word)
    if len(cons) != 4 or word[0] not in _IMPF_PREFORMATIVES:  # noqa: PLR2004
        return False
    if len(word) < 4:  # noqa: PLR2004
        return False
    if word[1] != HEB_DAGESH:
        return False
    if word[2] != "ו":
        return False
    return word[3] in (HEB_HOLAM, HEB_HOLAM_HASER)


def _is_hiphil_impf_bare(word: str) -> bool:
    """Hiphil imperfect bare form: preformative(patah/dagesh) + C₁(sheva/hataf) + C₂ + יod + C₃.

    5-consonant pattern: preformative(patah) + C₁(sheva) + C₂(hiriq) + י(mater) + C₃.
    Examples: יַמְטִיר (Hiphil impf 3ms of מטר), תַּצְמִיחַ (Hiphil impf 2ms/3fs of צמח).
    """
    cons = constanants(word)
    if len(cons) != 5 or cons[0] not in _IMPF_PREFORMATIVES or cons[3] != "י":  # noqa: PLR2004
        return False
    vowel_pref, _ = _first_vowel(word)
    if vowel_pref != HEB_PATAH:
        return False
    return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)


def _is_hiphil_impf_peyod(word: str) -> bool:
    """Pe-yod Hiphil imperfect: 5 consonants with preformative.

    Pattern A: preformative(tsere) + י(root pe-yod) + C₂(hiriq) + יod(mater) + C₃.
    E.g. תֵּיטִיב (Hiphil impf 3fs of יטב), יֵיטִיב (Hiphil impf 3ms of יטב).

    Pattern B: preformative(holam-vav) + ו(mater) + C₁(hiriq) + יod(mater) + C₂.
    E.g. יוֹסִיף (Hiphil impf 3ms of יסף), תּוֹסִיף (2ms).
    """
    cons = constanants(word)
    if len(cons) != 5 or cons[0] not in _IMPF_PREFORMATIVES:  # noqa: PLR2004
        return False
    vowel_pref, _ = _first_vowel(word)
    # Pattern A: tsere on preformative, pe-yod preserved as cons[1]
    if cons[1] == "י" and cons[3] == "י" and vowel_pref == HEB_TSERE:
        return True
    # Pattern B: holam-vav on preformative, cons[1]='ו', cons[3]='י'
    if cons[1] == "ו" and cons[3] == "י":
        if _vowel_at_consonant(word, 1) not in (HEB_HOLAM, HEB_HOLAM_HASER):
            return False
        return _vowel_at_consonant(word, 2) in (HEB_HIRIQ, HEB_TSERE, HEB_SHEVA, *_HATAF_VOWELS)
    return False


def _is_hiphil_perf_peyod(word: str) -> bool:
    """Pe-yod Hiphil perfect: ה + ו(holam-vav mater) + C₁ + [יod] + C₂.

    Standard (5 cons): ה + ו(holam-vav) + C₁(hiriq/tsere) + יod(mater) + C₂.
    Pe-aleph lamed (4 cons): ה + ו(holam-vav) + C₁(tsere/hiriq) + א(quiescent).
    Examples: הוֹלִיד (ילד), הוֹצִיא (יצא), הוֹשִׁיבַ- (ישׁב), הוֹצֵא (stem of הוֹצִיא).
    """
    cons = constanants(word)
    if not cons or cons[0] != "ה" or (len(cons) >= 2 and cons[1] != "ו"):  # noqa: PLR2004
        return False
    if _vowel_at_consonant(word, 1) not in (HEB_HOLAM, HEB_HOLAM_HASER):
        return False
    # 5-cons: ה + ו(holam) + C₁(hiriq/tsere) + יod(mater) + C₂
    if len(cons) == 5 and cons[3] == "י":  # noqa: PLR2004
        return _vowel_at_consonant(word, 2) in (HEB_HIRIQ, HEB_TSERE, HEB_SHEVA, *_HATAF_VOWELS)
    # 4-cons: ה + ו(holam) + C₁(tsere/hiriq) + C₂ (incl. lamed-aleph: C₂=א quiescent)
    if len(cons) == 4:  # noqa: PLR2004
        return _vowel_at_consonant(word, 2) in (HEB_HIRIQ, HEB_TSERE, HEB_SEGOL, HEB_SHEVA, *_HATAF_VOWELS)
    return False


def _is_piel_perf_stem(stem: str) -> bool:
    """Piel/Pual-like perfect stem: 3 (or 2) consonants with hiriq/tsere on C₁ and dagesh on C₂.

    Used in the suffixed-perfect loop to identify Piel non-3ms forms.
    The dagesh forte on C₂ is the definitive Piel marker; hiriq/tsere on C₁ is diagnostic.
    Examples: שִׁלַּחְ (from שִׁלַּחְתִּי), בֵּרַכְ (from בֵּרַכְתָּ).
    """
    cons = constanants(stem)
    if len(cons) not in (2, 3):
        return False
    vowel, _ = _first_vowel(stem)
    if vowel not in (HEB_HIRIQ, HEB_TSERE):
        return False
    return _has_dagesh_at(stem, 1)


def _is_hiphil_part_peyod(word: str) -> bool:
    """Pe-yod/hollow/pe-nun Hiphil participle ms, 4 or 5 consonants.

    4-cons: מ(tsere/segol) + C₁(hiriq) + יod + C₂ — pe-yod/hollow pattern.
    4-cons: מ(patah) + C₁(hiriq+dagesh = assimilated nun) + יod + C₂ — pe-nun pattern.
    5-cons: מ + ו(holam-vav) + C₁(hiriq) + יod + C₂ — pe-yod with holam-vav mater.
    Examples: מֵבִיא (בוא), מֵשִׁיב (שׁוב), מוֹשִׁיעַ (ישׁע), מַגִּיד (נגד), מַצִּיל (נצל).
    """
    cons = constanants(word)
    # 4-cons: מ(tsere/segol) + C₁(hiriq) + יod + C₂  — pe-yod/hollow
    if len(cons) == 4 and cons[0] == "מ" and cons[2] == "י":  # noqa: PLR2004
        vowel_mem, _ = _first_vowel(word)
        if vowel_mem in (HEB_TSERE, HEB_SEGOL):
            return _vowel_at_consonant(word, 1) in (HEB_HIRIQ, HEB_SHEVA, *_HATAF_VOWELS)
        # Pe-nun: מ(patah) + C₁(dagesh = assimilated nun, hiriq) + יod + C₂
        if vowel_mem == HEB_PATAH:
            return _vowel_at_consonant(word, 1) == HEB_HIRIQ
        return False
    # 5-cons: מ(no vowel) + ו(holam-vav) + C₁(hiriq) + יod + C₂
    if len(cons) == 5 and cons[0] == "מ" and cons[1] == "ו" and cons[3] == "י":  # noqa: PLR2004
        if _vowel_at_consonant(word, 1) not in (HEB_HOLAM, HEB_HOLAM_HASER):
            return False
        return _vowel_at_consonant(word, 2) in (HEB_HIRIQ, HEB_SHEVA, *_HATAF_VOWELS)
    return False


def _is_qal_passive_part(word: str) -> bool:
    """Qal passive participle ms (qatûl): C₁(qamats) + C₂ + ו(shureq) + C₃, 4 consonants.

    The shureq (ו+dagesh) on C₃ is the diagnostic u-class vowel.
    Examples: כָּתוּב (written, from כתב), שָׁמוּר (guarded, from שׁמר).
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[2] != "ו" or cons[-1] == "ה":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 != HEB_QAMATS:
        return False
    # C₃ (ו) must have shureq (dagesh following ו)
    return _has_shureq(word, 2)


def _is_qal_passive_part_fs(word: str) -> bool:
    """Qal passive participle fs (qatûlāh): C₁(qamats/hataf) + C₂ + ו(shureq) + C₃ + ה, 5 cons.

    Examples: אֲרוּרָה (cursed, fs), כְּתוּבָה (written, fs).
    """
    cons = constanants(word)
    if len(cons) != 5 or cons[2] != "ו" or cons[-1] != "ה":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in (HEB_QAMATS, *_HATAF_VOWELS):
        return False
    return _has_shureq(word, 2)


def _is_qal_imp_holam_vav(word: str) -> bool:
    """Qal imperative/inf absolute with holam-vav: C₁(sheva/hataf) + C₂ + ו(holam) + C₃, 4 cons.

    The ו carries holam (holam-vav mater), making 4 consonants.
    Examples: שְׁמוֹר (Qal imp of שׁמר), כְּתוֹב (Qal imp/inf-abs of כתב).
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[2] != "ו" or cons[-1] == "ה":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    if vowel_c1 not in (HEB_SHEVA, *_HATAF_VOWELS):
        return False
    return _vowel_at_consonant(word, 2) == HEB_HOLAM


def _is_pe_yod_impf_hollow(word: str) -> bool:
    """Pe-yod/hollow imperfect: preformative + ו(holam-vav/shureq) + C₁ + C₂, 4 consonants.

    The ו acts as holam-vav/shureq mater on the preformative (pe-yod dropped).
    Examples: תּוּכַל (2ms of יכל), יוּכַל (3ms), אוּכַל (1cs).
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[0] not in _IMPF_PREFORMATIVES or cons[1] != "ו":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c2 = _vowel_at_consonant(word, 1)
    return vowel_c2 == HEB_HOLAM or (vowel_c2 is None and _has_shureq(word, 1))


def _is_niphal_perf_peyod(word: str) -> bool:
    """Pe-yod Niphal perfect 3ms: נ + ו(holam-vav mater) + C₁(qamats) + C₂, 4 consonants.

    The pe-yod dropped and נ carries holam-vav as the Niphal vowel.
    Examples: נוֹתָר (remained, Niphal of יתר), נוֹלַד (born, Niphal of ילד).
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[0] != "נ" or cons[1] != "ו":  # noqa: PLR2004
        return False
    if _vowel_at_consonant(word, 1) not in (HEB_HOLAM, HEB_HOLAM_HASER):
        return False
    return _vowel_at_consonant(word, 2) in (HEB_QAMATS, HEB_PATAH, HEB_TSERE)


def _is_niphal_part_mp(word: str) -> bool:
    """Niphal participle mp: 6 consonants ending ים.

    Regular: נ(hiriq/hataf) + C₁(sheva/hataf) + C₂ + C₃ + ים.
    Pe-yod: נ(no vowel) + ו(holam-vav) + C₁(qamats/patah) + C₂ + ים.
    Examples: נִשְׁאָרִים (remaining, שׁאר), נּוֹתָרִים (pe-yod, יתר).
    """
    cons = constanants(word)
    if len(cons) != 6 or cons[-2] != "י" or cons[-1] != "ם":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    if cons[0] != "נ":
        return False
    # Pe-yod variant: נ + ו(holam-vav) + C₁ + C₂ + ים
    if cons[1] == "ו":
        if _vowel_at_consonant(word, 1) not in (HEB_HOLAM, HEB_HOLAM_HASER):
            return False
        return _vowel_at_consonant(word, 2) in (HEB_QAMATS, HEB_TSERE, HEB_PATAH, *_HATAF_VOWELS)
    # Regular: נ(hiriq) + C₁(sheva/hataf) + C₂ + C₃ + ים
    vowel_n, _ = _first_vowel(word)
    if vowel_n not in (HEB_HIRIQ, *_HATAF_VOWELS):
        return False
    return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)


def _is_niphal_part_fp(word: str) -> bool:
    """Niphal participle fp: 6 consonants ending ות.

    Regular: נ(hiriq) + C₁(sheva/hataf) + C₂(qamats/tsere) + C₃ + וֹת.
    Examples: נִפְלָאוֹת (wonderful things, root פלא), נִבְחָרוֹת (chosen, root בחר).
    """
    cons = constanants(word)
    if len(cons) != 6 or cons[-2] != "ו" or cons[-1] != "ת":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    if cons[0] != "נ":
        return False
    vowel_n, _ = _first_vowel(word)
    if vowel_n not in (HEB_HIRIQ, *_HATAF_VOWELS):
        return False
    return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)


def _is_qal_part_mp(word: str) -> bool:
    """Qal active participle mp: C₁(holam) + C₂ + C₃ + ִים (5 consonants, C4='י', C5='ם').

    Examples: צֹעֲקִים (crying out), שֹׁמְרִים (guarding), etc.
    """
    cons = constanants(word)
    if len(cons) != 5 or cons[3] != "י" or cons[4] != "ם":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    return vowel_c1 == HEB_HOLAM


def _is_segol_segol_inf(word: str) -> bool:
    """Irregular infinitive construct: C₁(segol)C₂(segol)C₃, 3 consonants.

    Catches the irregular inf construct of הלך (לֶכֶת) and similar.
    """
    cons = constanants(word)
    if len(cons) != 3:  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_c1, _ = _first_vowel(word)
    return vowel_c1 == HEB_SEGOL and _vowel_at_consonant(word, 1) == HEB_SEGOL


def _is_hitpael_perf(word: str) -> bool:
    """Hitpael/Hitpoel/Hishtaphel perfect 3ms: ה(hiriq) + ת(sheva) + root (5+ consonants).

    Standard Hitpael: ה + ת(sheva) prefix.
    Hishtaphel (sibilant metathesis): ה + שׁ(sheva) + ת prefix (e.g. הִשְׁתַּחֲוָה from שׁחה).
    """
    cons = constanants(word)
    if len(cons) < 5 or cons[0] != "ה":  # noqa: PLR2004
        return False
    vowel_h, _ = _first_vowel(word)
    if vowel_h != HEB_HIRIQ:
        return False
    if cons[1] == "ת":
        return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)
    # Hishtaphel: ה + ש(sheva) + ת
    if cons[1] == "ש" and len(cons) > 2 and cons[2] == "ת":  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) == HEB_SHEVA
    return False


def _strip_final_consonants(word: str, n: int) -> str | None:
    """Strip the last n consonants and any diacritics that follow them."""
    count = 0
    for i in range(len(word) - 1, -1, -1):
        if is_consanant(word[i]):
            count += 1
            if count == n:
                return word[:i]
    return None


def _is_niphal_perf_4cons(word: str) -> bool:
    """Niphal perfect bare stem: נ(hiriq) + C₁(sheva/hataf) + C₂ + C₃, 4 consonants.

    Catches regular Niphal perfect 3ms: נִשְׁמַר, נִפְקַח, etc.
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[0] != "נ":  # noqa: PLR2004
        return False
    vowel_n, _ = _first_vowel(word)
    if vowel_n != HEB_HIRIQ:
        return False
    return _vowel_at_consonant(word, 1) in (HEB_SHEVA, *_HATAF_VOWELS)


def _is_niphal_inf_construct(word: str) -> bool:
    """Niphal infinitive construct: ה(hiriq) + C₁(full vowel) + C₂(sheva/hataf) + C₃, 4 cons.

    The dagesh forte in C₁ (Niphal characteristic) causes C₁ to take a full vowel
    rather than sheva.  Distinguishes from Hiphil by C₂ having sheva (not a yod mater).
    Examples: הִבָּרֵא (Niphal inf of ברא), הִלָּחֵם (Niphal inf of לחם).
    """
    cons = constanants(word)
    if len(cons) != 4 or cons[0] != "ה":  # noqa: PLR2004
        return False
    vowel_h, _ = _first_vowel(word)
    if vowel_h != HEB_HIRIQ:
        return False
    # C₁ must have a full vowel (not sheva) — the Niphal dagesh forte yields patah/qamats/tsere
    vowel_c1 = _vowel_at_consonant(word, 1)
    if vowel_c1 not in (HEB_QAMATS, HEB_PATAH, HEB_TSERE, HEB_HIRIQ):
        return False
    # C₂ must have sheva, hataf, or a full vowel before guttural (distinguishes from Hiphil)
    # Tsere/segol/patah on C₂ can appear when C₂ is a guttural (e.g. הִנָּבֵא, הִלָּחֵם)
    vowel_c2 = _vowel_at_consonant(word, 2)
    return vowel_c2 in (HEB_SHEVA, HEB_TSERE, HEB_SEGOL, HEB_PATAH, *_HATAF_VOWELS)


def _is_3cons_impf_stem(stem: str, check_bdb: bool = True) -> bool:
    """3-consonant imperfect stem after suffix stripping (pe-yod/pe-nun/hollow verbs).

    Validates stems where the first root consonant dropped or assimilated, leaving
    only preformative + 2 root consonants.  Set check_bdb=False when a suffix has
    already been stripped (the suffix itself provides strong imperfect evidence).
    """
    cons = constanants(stem)
    if len(cons) != 3 or stem[0] not in _IMPF_PREFORMATIVES:  # noqa: PLR2004
        return False
    if check_bdb and cons in _BDB_NOUN_LEMMAS:
        return False
    vowel, _ = _first_vowel(stem)
    return vowel in _3CONS_IMPF_PREFORMATIVE_VOWELS


def _is_hitpael_impf(word: str) -> bool:
    """Hitpael/Hitpoel/Hitpalpel/Hishtaphel imperfect: preformative(hiriq) + ת(sheva) + root, 5+ cons.

    Standard: preformative + ת(sheva) + root (Hitpael).
    Hishtaphel (sibilant metathesis): preformative + שׁ(sheva) + ת + root, where the
    sibilant שׁ/שׂ/ס/צ swaps with the Hitpael ת (e.g. יִשְׁתַּחֲווּ from שׁחה).
    """
    cons = constanants(word)
    if len(cons) < 5 or cons[0] not in _IMPF_PREFORMATIVES:  # noqa: PLR2004
        return False
    vowel_pref, _ = _first_vowel(word)
    if vowel_pref != HEB_HIRIQ:
        return False
    # Standard Hitpael: preformative + ת(sheva)
    if cons[1] == "ת":
        return _vowel_at_consonant(word, 1) == HEB_SHEVA
    # Hishtaphel (sibilant metathesis): preformative + ש/שׁ(sheva) + ת
    if cons[1] == "ש" and len(cons) > 2 and cons[2] == "ת":  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) == HEB_SHEVA
    return False


def _is_hitpael_part(word: str) -> bool:
    """Hitpael/Hitpoel/Hishtaphel participle ms: מ(hiriq) + ת(sheva) + root, 5+ consonants.

    Standard Hitpael: מ + ת(sheva) prefix.
    Hishtaphel: מ + שׁ(sheva) + ת prefix (sibilant metathesis).
    """
    cons = constanants(word)
    if len(cons) < 5 or cons[0] != "מ":  # noqa: PLR2004
        return False
    vowel_mem, _ = _first_vowel(word)
    if vowel_mem != HEB_HIRIQ:
        return False
    if cons[1] == "ת":
        return _vowel_at_consonant(word, 1) == HEB_SHEVA
    # Hishtaphel: מ + ש(sheva) + ת
    if cons[1] == "ש" and len(cons) > 2 and cons[2] == "ת":  # noqa: PLR2004
        return _vowel_at_consonant(word, 1) == HEB_SHEVA
    return False


def _is_niphal_inf_lamedhe(word: str) -> bool:
    """Niphal infinitive construct of lamed-he roots: ה(tsere/hiriq) + C₁ + C₂ + ו(holam) + ת, 5 cons.

    The ות ending is characteristic of the Niphal inf construct for lamed-he roots.
    Examples: הֵעָלוֹת (Niphal inf of עלה), הִלָּחֵם (Niphal inf of לחם — 4 cons handled separately).
    """
    cons = constanants(word)
    if len(cons) != 5 or cons[0] != "ה" or cons[3] != "ו" or cons[4] != "ת":  # noqa: PLR2004
        return False
    vowel_h, _ = _first_vowel(word)
    if vowel_h not in (HEB_TSERE, HEB_HIRIQ, HEB_SEGOL):
        return False
    return _vowel_at_consonant(word, 1) is not None


def _is_polel_part_mp(word: str) -> bool:
    """Polel/Poel participle mp: מְ + C₁(holam) + C₁/C₂ + שׁוּרֵק + ִים (6 consonants).

    Catches forms like מְשֹׁרְרִים (singers, Polel part mp of שׁיר/שׁרר).
    Pattern: 6 consonants, cons[0]='מ', cons[-2]='י', cons[-1]='ם'.
    """
    cons = constanants(word)
    if len(cons) != 6 or cons[0] != "מ" or cons[-2] != "י" or cons[-1] != "ם":  # noqa: PLR2004
        return False
    if cons in _BDB_NOUN_LEMMAS:
        return False
    vowel_mem, _ = _first_vowel(word)
    if vowel_mem != HEB_SHEVA:
        return False
    return _vowel_at_consonant(word, 1) in (HEB_HOLAM, HEB_HOLAM_HASER, HEB_QAMATS, *_HATAF_VOWELS)


def is_verb(elements: CommonElements, _depth: int = 0) -> HebVerb | None:  # noqa: PLR0912, C901, PLR0911
    """Is the word a Verb?"""
    word = elements.word
    cons_word = constanants(word)

    # Try each perfect suffix (longest first to avoid partial matches)
    word_nfd = unicodedata.normalize("NFD", word)
    for suffix, person, gender, number in _PERF_SUFFIXES:
        suffix_nfd = unicodedata.normalize("NFD", suffix)
        if word_nfd.endswith(suffix_nfd) and _is_valid_perf_stem(
            word_nfd[: -len(suffix_nfd)]
        ):
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
                word_constanants=constanants(
                    unicodedata.normalize("NFC", word_nfd[: -len(suffix_nfd)])
                ),
            )

    # Niphal/Hiphil/Hitpael perfect suffixed forms
    for suffix, person, gender, number in _PERF_SUFFIXES:
        suffix_nfd = unicodedata.normalize("NFD", suffix)
        if word_nfd.endswith(suffix_nfd):
            stem_nfd = word_nfd[: -len(suffix_nfd)]
            stem_nfc = unicodedata.normalize("NFC", stem_nfd)
            for stem_check in (_is_niphal_perf_4cons, _is_hiphil_perf_3ms, _is_hitpael_perf, _is_hiphil_perf_peyod, _is_piel_perf_stem):
                if stem_check(stem_nfc):
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
                        word_constanants=constanants(stem_nfc),
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
            if stem and stem[0] == expected_preformative and (
                _is_valid_impf_stem(stem)
                or _is_3cons_impf_stem(stem, check_bdb=False)
                or _is_hitpael_impf(stem)
                or _is_hiphil_impf_bare(stem)
                or _is_hiphil_impf_peyod(stem)
            ):
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
                    word_constanants=constanants(stem)[1:],
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
                    word_constanants=constanants(word)[1:],
                )

    # Hitpael/Hitpoel bare imperfect: preformative(hiriq) + ת(sheva) + root (5+ cons)
    if _is_hitpael_impf(word):
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
                    word_constanants=constanants(word)[1:],
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

    # Qal active participle ms with holam-vav: C₁(no-vowel)+ו(holam)+C₂(tsere)+C₃ (e.g. רוֹמֵשׂ)
    if _is_qal_part_ms_holam_vav(word):
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

    # Qal active participle mp: C₁(holam) + C₂ + C₃ + ִים (e.g. צֹעֲקִים)
    if _is_qal_part_mp(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="p",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word[:-2],  # strip יִם
        )

    # Qal active participle fs: C₁(holam)C₂C₃ + ת (e.g. רֹמֶשֶׂת)
    if _is_qal_part_fs(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="f",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word)[:-1],  # strip ת suffix
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

    # Qal imperative 2mp: C₁(sheva)C₂ + וּ (e.g. רְדוּ from ירד, לְכוּ from הלך)
    if _is_qal_imp_plural(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood="imperative",
            number="p",
            person="2",
            preposition=elements.preposition,
            raw=elements.raw,
            tense=None,
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word)[:-1],  # strip ו suffix
        )

    # Ayin-vav/ayin-yod inf construct / imperative: C₁(holam) + C₂(ו/י) + C₃ (e.g. בוֹא)  # noqa: RUF003
    if _is_ayin_vav_inf(word):
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

    # Lamed-he Qal perfect 2ms/2fs (e.g. עָשִׂיתָ, עָשִׂית from עָשָׂה)
    result_lhe = _is_lamed_he_perf(word)
    if result_lhe:
        person, gender, number = result_lhe
        cons_lhe = constanants(word)
        # Strip יתי (1cs) or יתם/יתן (2mp/2fp) — 3 cons — or ית (2ms/2fs) — 2 cons
        root_lhe = cons_lhe[:-3] + "ה" if (person == "1" or number == "p") else cons_lhe[:-2] + "ה"
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
            word_constanants=root_lhe,
        )

    # Pual perfect 3ms: C₁(qubuts) + C₂(dagesh) + C₃ (e.g. צֻוָּה)
    if _is_pual_perf(word):
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

    # Piel form: C₁(patah/hiriq) + C₂(tsere) + C₃ (e.g. צַוֵּה)
    if _is_piel_form(word):
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

    # Lamed-nun Qal perfect 1cs with assimilated final nun (e.g. נָתַתִּי from נָתַן)
    if _is_lamed_nun_perf_1cs(word):
        # Consonants are C₁+C₂(=ת)+ת+י; restore the final nun: C₁C₂ → C₁C₂ן
        return HebVerb(
            definite_article=elements.definite_article,
            gender="c",
            mood=None,
            number="s",
            person="1",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="perfect",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word)[:-2] + "ן",
        )

    # Hollow verb (ayin-vav/ayin-yod) 2-consonant Qal forms (e.g. בָּא, בֹּא)
    result = _is_hollow_qal(word)
    if result:
        tense, mood, person, gender, number = result
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

    # Hiphil perfect 3ms: ה(hiriq) + C₁(sheva) + C₂ + י + C₃ (e.g. הִמְטִיר, הִשְׁקָה)
    if _is_hiphil_perf_3ms(word):
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

    # Hiphil active participle ms: מַ + C₁(sheva) + C₂ + יod + C₃
    if _is_hiphil_part_ms(word):
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

    # Pe-yod/hollow Hiphil perfect 3ms: ה(holam-vav) + ו + C₁(hiriq) + י + C₂ (e.g. הוֹלִיד)
    if _is_hiphil_perf_peyod(word):
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
            word_constanants=cons_word,
        )

    # Pe-yod/hollow Hiphil participle ms: מ(tsere) + C₁(hiriq) + יod + C₂ (e.g. מֵבִיא)
    if _is_hiphil_part_peyod(word):
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
            word_constanants=cons_word,
        )

    # Hiphil imperfect bare form: preformative(patah) + C₁(sheva) + C₂ + יod + C₃ (e.g. יַמְטִיר)
    if _is_hiphil_impf_bare(word):
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
                    word_constanants=cons_word[1:],
                )

    # Pe-yod Hiphil imperfect: preformative(tsere) + י(root) + C₂(hiriq) + יod + C₃ (e.g. תֵּיטִיב)
    if _is_hiphil_impf_peyod(word):
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
                    word_constanants=cons_word[1:],
                )

    # Hiphil infinitive construct
    if _is_hiphil_inf(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="",
            mood="construct",
            number="",
            person="",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="infinitive",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=constanants(word),
        )

    # Hitpael/Hitpoel perfect 3ms: ה(hiriq) + ת(sheva) + root (5+ consonants)
    if _is_hitpael_perf(word):
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
            word_constanants=cons_word,
        )

    # Niphal perfect 3ms (regular 4-consonant form): נ(hiriq) + C₁(sheva) + C₂ + C₃
    if _is_niphal_perf_4cons(word):
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
            word_constanants=cons_word,
        )

    # Niphal infinitive construct of lamed-he roots: ה(tsere) + C₁ + C₂ + ו(holam) + ת (e.g. הֵעָלוֹת)
    if _is_niphal_inf_lamedhe(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="",
            mood="construct",
            number="",
            person="",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="infinitive",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word,
        )

    # Polel/Poel participle mp: מְ + root + ִים, 6 consonants (e.g. מְשֹׁרְרִים)
    if _is_polel_part_mp(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="p",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word[1:-2],  # strip מ prefix and ים suffix
        )

    # Niphal infinitive construct: ה(hiriq) + C₁(full vowel) + C₂(sheva) + C₃
    if _is_niphal_inf_construct(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="",
            mood="construct",
            number="",
            person="",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="infinitive",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word,
        )

    # Hitpael/Hitpoel participle ms: מ(hiriq) + ת(sheva) + root (5+ consonants)
    if _is_hitpael_part(word):
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
            word_constanants=cons_word,
        )

    # Piel participle ms/fs: מְ(sheva) + C₁(patah) + C₂ + C₃ [+ ת]
    if _is_piel_part(word):
        cons_piel = constanants(word)
        return HebVerb(
            definite_article=elements.definite_article,
            gender="f" if len(cons_piel) == 5 else "m",  # noqa: PLR2004
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_piel,
        )

    # Qal passive participle ms (qatûl): C₁(qamats) + C₂ + ו(shureq) + C₃
    if _is_qal_passive_part(word):
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
            word_constanants=cons_word,
        )

    # Qal passive participle fs (qatûlāh): C₁(qamats/hataf) + C₂ + ו(shureq) + C₃ + ה
    if _is_qal_passive_part_fs(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="f",
            mood=None,
            number="s",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word[:-1],  # strip ה suffix
        )

    # Qal imperative/inf-abs with holam-vav: C₁(sheva/hataf) + C₂ + ו(holam) + C₃
    if _is_qal_imp_holam_vav(word):
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
            word_constanants=cons_word,
        )

    # Pe-yod/hollow imperfect with holam-vav/shureq preformative: pref + ו + C₁ + C₂
    if _is_pe_yod_impf_hollow(word):
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
                    word_constanants=cons_word[1:],
                )

    # Pe-yod Niphal perfect 3ms: נ + ו(holam-vav) + C₁(qamats) + C₂
    if _is_niphal_perf_peyod(word):
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
            word_constanants=cons_word,
        )

    # Niphal participle mp: נ(hiriq) + C₁(sheva) + C₂ + C₃ + ים (regular), or
    # pe-yod: נ + ו(holam-vav) + C₁ + C₂ + ים
    if _is_niphal_part_mp(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="m",
            mood=None,
            number="p",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word[:-2],  # strip ים
        )

    # Niphal participle fp: נ(hiriq) + C₁(sheva) + C₂ + C₃ + וֹת
    if _is_niphal_part_fp(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="f",
            mood=None,
            number="p",
            person="3",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="participle",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word[:-2],  # strip ות
        )

    # Irregular inf construct: C₁(segol)C₂(segol)C₃ (e.g. לֶכֶת = inf of הלך)
    if _is_segol_segol_inf(word):
        return HebVerb(
            definite_article=elements.definite_article,
            gender="",
            mood="construct",
            number="",
            person="",
            preposition=elements.preposition,
            raw=elements.raw,
            tense="infinitive",
            vav_consec=elements.vav_consec,
            word=word,
            word_constanants=cons_word,
        )

    # Hollow Hiphil imperfect: preformative(dagesh) + ו(holam) + C₂ + C₃
    if _is_hollow_hiphil_impf(word):
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
                    word_constanants=constanants(word)[1:],
                )

    # Cohortative / paragogic ה: word ends in ָה (qamats + ה); strip it and test as imperfect
    # or imperative.  The 3fs perfect suffix is identical but is caught earlier by _PERF_SUFFIXES.
    if _depth == 0:
        word_nfd_coh = unicodedata.normalize("NFD", word)
        _coh = unicodedata.normalize("NFD", HEB_QAMATS + "ה")
        if word_nfd_coh.endswith(_coh) and len(word_nfd_coh) > len(_coh):
            stem_coh = unicodedata.normalize("NFC", word_nfd_coh[: -len(_coh)])
            if stem_coh:
                coh_bare = CommonElements(
                    word=stem_coh,
                    raw=elements.raw,
                    preposition=elements.preposition,
                    definite_article=elements.definite_article,
                    vav_consec=elements.vav_consec,
                )
                r_coh = is_verb(coh_bare, _depth=1)
                if r_coh:
                    return HebVerb(
                        definite_article=r_coh.definite_article,
                        gender=r_coh.gender,
                        mood=r_coh.mood if r_coh.tense != "perfect" else "cohortative",
                        number=r_coh.number,
                        person=r_coh.person,
                        preposition=r_coh.preposition,
                        raw=elements.raw,
                        tense=r_coh.tense if r_coh.tense != "perfect" else "imperfect",
                        vav_consec=r_coh.vav_consec,
                        word=word,
                        word_constanants=r_coh.word_constanants,
                    )

    # Try verb forms with pronominal object suffixes (ך 2ms, נו 3ms-suffix, ני 1cs-suffix).
    # Strip the suffix consonant(s), re-run verb recognition at depth=1 to avoid recursion.
    # Skip if the full word's consonants are a known BDB noun/adj lemma — the suffix would
    # be part of the root (e.g. אֱלֹהִים ends in ם but is a noun, not a verb+ם suffix).
    if _depth == 0 and cons_word not in _BDB_NOUN_LEMMAS:
        for suf_cons, strip_n in (("ך", 1), ("נו", 2), ("ני", 2), ("הו", 2), ("ם", 1), ("ו", 1), ("י", 1)):
            if cons_word.endswith(suf_cons) and len(cons_word) > strip_n + 2:
                stripped = _strip_final_consonants(word, strip_n)
                if stripped:
                    bare = CommonElements(
                        word=stripped,
                        raw=elements.raw,
                        preposition=elements.preposition,
                        definite_article=elements.definite_article,
                        vav_consec=elements.vav_consec,
                    )
                    result_suf = is_verb(bare, _depth=1)
                    if result_suf:
                        return HebVerb(
                            definite_article=result_suf.definite_article,
                            gender=result_suf.gender,
                            mood=result_suf.mood,
                            number=result_suf.number,
                            person=result_suf.person,
                            preposition=result_suf.preposition,
                            raw=elements.raw,
                            tense=result_suf.tense,
                            vav_consec=result_suf.vav_consec,
                            word=word,
                            word_constanants=result_suf.word_constanants,
                        )

    return None
