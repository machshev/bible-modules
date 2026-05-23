"""Preposition parser."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

HEBREW_PRONOUNS = (
    # Relative pronoun
    "אָשֵׁר",  # That
    # Personal pronouns
    "אֲנִי",  # I (1c)
    "אָנֹכִי",  # I (1c)
    "אַתָּה",  # You (2ms)
    "אַתְּ",  # You (2fs)
    "הוּא",  # He/it (3m)
    "הִיא",  # She (3f)
    "אֲנַחְנוּ",  # We (1cp)
    "אַתֶּם",  # You (2mp)
    "אַתֵּן",  # You (2fp)
    "הֵם",  # They (3mp)
    "הֵן",  # They (3fp)
    # Demonstrative pronouns
    "זֶה",  # This (m)
    "זֹאת",  # This (f)
    "אֵלֶּה",  # These (cp)
    "הֵמָּה",  # Those (mp)
    "הֵנָּה",  # Those (fp)
    # Interrogative
    "מִי",
    "מָה",
    "מַה",
    "לָמָה",  # why? (ל+מה)
    "אַיֵּה",
    "אֵי",
    # Indefinite pronouns
    "כָל",  # All
    # Pronominal suffix (1cs) — also catches construct plural of בן after ב-strip
    "נִי",  # me / my
    # Object pronoun / preposition with 3ms suffix
    "אֹתוֹ",  # him / it (direct object marker + 3ms; also אִתּוֹ with him)
    # Preposition ב + 3fs pronominal suffix הּ ("in her/it")
    # Covers בַהּ, בָּהּ, בֵּהּ, בֵהּ — all share consonants בה
    "בַהּ",
    # 3fs pronominal suffix הּ alone (after preposition is stripped, e.g. לָּהּ → הּ)
    "הּ",
    # Direct object pronoun 3mp אוֹתָם (ʾōtām); consonants אותם  # noqa: RUF003
    "אוֹתָם",
    # Direct object pronoun 3fp אוֹתָן (ʾōtān); consonants אותן  # noqa: RUF003
    "אוֹתָן",
    # Preposition ב + 1cs suffix י ("in me / by me"); covers בִּי and בִי
    "בִּי",
    # 1cp pronominal suffix נוּ ("us/our"), e.g. לָנוּ, בָּנוּ
    "נוּ",
)
HEBREW_PRONOUNS_CONST = tuple(constanants(w) for w in HEBREW_PRONOUNS)

__all__ = (
    "HebPronoun",
    "is_pronoun",
)


@dataclass(frozen=True)
class HebPronoun:
    """Hebrew Pronoun."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None


def is_pronoun(elements: CommonElements) -> HebPronoun | None:
    """Is the word a Pronoun."""
    if constanants(elements.word) not in HEBREW_PRONOUNS_CONST:
        return None

    return HebPronoun(
        preposition=elements.preposition,
        vav_consec=elements.vav_consec,
        definite_article=elements.definite_article,
        word=elements.word,
        word_constanants=constanants(elements.word),
        raw=elements.raw,
    )
