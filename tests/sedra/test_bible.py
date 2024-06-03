"""Test that the SEDRA3 DB import functions are working."""

import pytest
from hamcrest import assert_that, calling, equal_to, raises

from bm_tools.sedra.bible import (
    SEDRAPassageRef,
    WordRefTuple,
    _parse_sedra3_word_address,
    _parse_sedra3_word_ref,
)

# ruff: noqa: D205


@pytest.mark.parametrize(
    ("word_ref", "expected_tuple"),
    [
        ("520100101", (SEDRAPassageRef(52, 1, 1), 1)),
        ("632198434", (SEDRAPassageRef(63, 21, 984), 34)),
        ("230001245", (SEDRAPassageRef(23, 0, 12), 45)),
    ],
)
def test_parse_sedra3_valid_word_ref(
    word_ref: str,
    expected_tuple: WordRefTuple,
) -> None:
    """Test that given a string of the correct format then a cosponsoring
    tuple of integers is returned.
    """
    assert_that(_parse_sedra3_word_ref(word_ref), equal_to(expected_tuple))


@pytest.mark.parametrize(
    ("word_ref", "expected_error_type", "expected_error_msg"),
    [
        ("", ValueError, "Expected word_ref of 9 characters"),
        ("df", ValueError, "Expected word_ref of 9 characters"),
        ("345634676734", ValueError, "Expected word_ref of 9 characters"),
        ("dfbgs_rjg", ValueError, ""),
    ],
)
def test_parse_sedra3_invalid_word_ref(
    word_ref: str,
    expected_error_type: type[Exception],
    expected_error_msg: str,
) -> None:
    """Test that when an invalid string the appropriate error is raised."""
    assert_that(
        calling(_parse_sedra3_word_ref).with_args(word_ref),
        raises(expected_error_type, expected_error_msg),
    )


@pytest.mark.parametrize(
    ("word_address", "expected_id"),
    [
        ("33565194", 10762),
    ],
)
def test_parse_sedra3_word_address(word_address: str, expected_id: int) -> None:
    """Test that given a string of the correct format then a cosponsoring id is
    returned.
    """
    assert_that(
        _parse_sedra3_word_address(word_address),
        equal_to(expected_id),
    )


def test_parse_sedra3_bible_db_file() -> None:
    """Test that ..."""
