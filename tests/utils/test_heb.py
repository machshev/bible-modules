"""Test hebrew utilities."""

import pytest
from hamcrest import assert_that, equal_to

from bm_tools.utils.heb import parse_definite_article


@pytest.mark.parametrize(
    ("raw", "word", "definite_article"),
    [
        ("", "", False),
        ("הַשָּׁמַיִם", "שָׁמַיִם", True),  # Normal consonant
        ("הָאָרֶץ", "אָרֶץ", True),  # Weak guteral
        ("הַחֹשֶׁךְ", "חֹשֶׁךְ", True),  # Strong guteral
        ("הָיוּ", "הָיוּ", False),  # Not a definite article
        ("הֶחָצֵר", "חָצֵר", True),  # Segol following Chet Qamats
        ("הָהָרָה", "הָרָה", True),  # Qamats following acented Hey Qamatz
    ],
)
def test_parse_definite_article(raw: str, word: str, definite_article: bool) -> None:  # noqa: FBT001
    """Test the definite article is correctly parsed."""
    actual_word, actual_definite_article = parse_definite_article(raw=raw)

    assert_that(actual_definite_article, equal_to(definite_article))
    assert_that(list(actual_word), equal_to(list(word)))
