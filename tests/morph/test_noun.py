"""Test noun morphology parsing."""

import pytest
from hamcrest import assert_that, equal_to, instance_of

from bm_tools.morph import morph_eval
from bm_tools.morph.noun import HebNoun


@pytest.mark.parametrize(
    ("raw", "gender", "number", "lemma"),
    [
        # Masculine singular base forms
        ("רָקִיעַ", "m", "s", "רקיע"),       # firmament
        ("מָאוֹר", "m", "s", "מאור"),         # luminary
        ("כּוֹכָב", "m", "s", "כוכב"),        # star
        ("מִין", "m", "s", "מין"),            # kind/species
        # Masculine plural (ים ending)
        ("כּוֹכָבִים", "m", "p", "כוכב"),     # stars
        ("מוֹעֲדִים", "m", "p", "מועד"),      # appointed times
        # Feminine plural (ות ending, ת suffix on masculine stem)
        ("מְאוֹרֹת", "f", "p", "מאור"),       # luminaries FP
        ("תוֹלְדֹת", "f", "p", "תולד"),       # generations FP
        # Pronominal suffixes — gender/number from the base noun lemma
        ("לְמִינֵהוּ", "m", "s", "מין"),      # prep + its kind (3ms suffix)
        # Ordinal adjectives
        ("שְׁלִישִׁי", "m", "s", "שלישי"),    # third (MS)
        ("רְבִיעִי", "m", "s", "רביעי"),      # fourth (MS)
        ("חֲמִישִׁי", "m", "s", "חמישי"),     # fifth (MS)
        # With prefixes stripped
        ("הָרָקִיעַ", "m", "s", "רקיע"),      # def art + firmament
        ("לָרָקִיעַ", "m", "s", "רקיע"),      # prep + def art + firmament
        ("בִּרְקִיעַ", "m", "s", "רקיע"),     # prep + firmament
        ("וּלְמוֹעֲדִים", "m", "p", "מועד"),  # vav + prep + appointed-times
        ("לִמְאוֹרֹת", "f", "p", "מאור"),     # prep + luminaries
        ("הַכּוֹכָבִים", "m", "p", "כוכב"),   # def art + stars
    ],
)
def test_noun_recognised(raw: str, gender: str, number: str, lemma: str) -> None:
    """Common nouns, ordinals, and pronominal-suffixed forms are recognised."""
    result = morph_eval(raw=raw)
    assert_that(result, instance_of(HebNoun))
    assert_that(result.gender, equal_to(gender))
    assert_that(result.number, equal_to(number))
    assert_that(result.word_constanants, equal_to(lemma))
