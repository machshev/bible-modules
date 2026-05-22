"""Test verb morphology parsing."""

import pytest
from hamcrest import assert_that, equal_to, instance_of, none

from bm_tools.morph import morph_eval
from bm_tools.morph.verb import HebVerb


@pytest.mark.parametrize(
    ("raw", "person", "gender", "number"),
    [
        # Full Qal perfect paradigm for שמר (to guard/keep)
        ("שָׁמַר", "3", "m", "s"),    # 3ms  CāCaC (no suffix)
        ("שָׁמְרָה", "3", "f", "s"),   # 3fs  + ָה
        ("שָׁמַרְתָּ", "2", "m", "s"),  # 2ms  + ְתָּ
        ("שָׁמַרְתְּ", "2", "f", "s"),  # 2fs  + ְתְּ
        ("שָׁמַרְתִּי", "1", "c", "s"), # 1cs  + ְתִּי
        ("שָׁמְרוּ", "3", "c", "p"),    # 3cp  + וּ
        ("שְׁמַרְתֶּם", "2", "m", "p"), # 2mp  + ְתֶּם
        ("שְׁמַרְתֶּן", "2", "f", "p"), # 2fp  + ְתֶּן
        ("שָׁמַרְנוּ", "1", "c", "p"),  # 1cp  + ְנוּ
        # Common verb: אמר (to say) — 3ms
        ("אָמַר", "3", "m", "s"),
        # Stative e-class: כבד (to be heavy) — 3ms CāCēC
        ("כָּבֵד", "3", "m", "s"),
    ],
)
def test_qal_perfect_regular(raw: str, person: str, gender: str, number: str) -> None:
    """Qal perfect regular (strong) verb forms are correctly parsed."""
    result = morph_eval(raw=raw)

    assert_that(result, instance_of(HebVerb))
    assert_that(result.tense, equal_to("perfect"))
    assert_that(result.person, equal_to(person))
    assert_that(result.gender, equal_to(gender))
    assert_that(result.number, equal_to(number))
    assert_that(result.mood, none())


def test_vav_consecutive_preserved() -> None:
    """Vav consecutive is stripped before verb detection and recorded on the verb."""
    result = morph_eval(raw="וַיֹּאמֶר")

    assert_that(result, instance_of(HebVerb))
    assert_that(result.tense, equal_to("imperfect"))
    assert_that(result.vav_consec, equal_to(True))


@pytest.mark.parametrize(
    ("raw", "person", "gender", "number"),
    [
        # Regular strong verb שׁמר (to guard)
        ("יִשְׁמֹר", "3", "m", "s"),    # 3ms
        ("תִּשְׁמֹר", "2", "m", "s"),   # 2ms (also 3fs)
        ("אֶשְׁמֹר", "1", "c", "s"),    # 1cs
        ("נִשְׁמֹר", "1", "c", "p"),    # 1cp
        ("יִשְׁמְרוּ", "3", "m", "p"),  # 3mp
        ("תִּשְׁמְרוּ", "2", "m", "p"), # 2mp
        ("תִּשְׁמְרִי", "2", "f", "s"), # 2fs
        # Pe-aleph verb אמר (to say) — preformative takes holem
        ("יֹאמַר", "3", "m", "s"),
        ("וַיֹּאמֶר", "3", "m", "s"),   # with vav-consecutive
        # Niphal imperfect pe-aleph אמר — preformative takes tsere
        ("יֵאָמַר", "3", "m", "s"),
    ],
)
def test_qal_imperfect_regular(raw: str, person: str, gender: str, number: str) -> None:
    """Imperfect verb forms are correctly parsed."""
    result = morph_eval(raw=raw)

    assert_that(result, instance_of(HebVerb))
    assert_that(result.tense, equal_to("imperfect"))
    assert_that(result.person, equal_to(person))
    assert_that(result.gender, equal_to(gender))
    assert_that(result.number, equal_to(number))
    assert_that(result.mood, none())


def test_preposition_preserved() -> None:
    """Inseparable ל preposition is stripped before verb detection and recorded."""
    # לְשָׁמְרָה = לְ + שָׁמְרָה (3fs perfect with ל preposition)
    result = morph_eval(raw="לְשָׁמְרָה")

    assert_that(result, instance_of(HebVerb))
    assert_that(result.preposition, equal_to("ל"))
    assert_that(result.tense, equal_to("perfect"))
    assert_that(result.person, equal_to("3"))
    assert_that(result.gender, equal_to("f"))
