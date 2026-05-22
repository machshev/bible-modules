"""Preposition parser."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

HEBREW_PREPOSITIONS = (
    "כִּי",  # For
    "עַל",  # Upon
    "אֶל",  # To
    "לֹא",  # No/Not
    "אַל",  # No/Not
    "עַד",  # Until
    "אִם",  # With
    "מִן",  # From
    "אַיִן",  # There is not
    "לוֹ",  # to him / if (לו — ל+3ms suffix or conditional particle)
    "לִי",  # to me (ל+1cs suffix; also catches כְּלֵי construct plural)
    "לְךָ",  # to you (ל+2ms/2fs suffix; also catches לֶךְ imperative of הלך)
    "לָכֶם",  # to you (2mp) — ל+כֶם
    "בָּכֶם",  # among you (2mp) — ב+כֶם
    "כָּכֶם",  # like you (2mp) — כ+כֶם
    "אֵלַי",  # to me — אֶל+1cs suffix (also catches other אלי forms)
    "עָלָיו",  # upon him/it — עַל+3ms suffix (also catches other עליו forms)
    "בוֹ",  # in him/it — ב+3ms suffix (consonants בו)
    "תַּחַת",  # under / beneath (preposition; also מִתַּחַת with מ prefix stripped)
    "עִמּוֹ",  # with him/it — עִם+3ms suffix (also catches עַמּוֹ his-people)
    "אֵלַיִךְ",  # to you (2fs) — אֶל+2fs suffix (consonants אליך)
    "עִמְּךָ",  # with you (2ms) — עִם+2ms suffix (also catches עַמְּךָ your-people)
    "עֲלֵיהֶם",  # upon them (3mp) — עַל+3mp suffix (consonants עליהם)
    "לָהּ",  # to her / for her — ל+3fs suffix (consonants לה; also catches כַּלָּה stripped forms)  # noqa: E501
    "לָנוּ",  # to us — ל+1cp suffix (also בָּנוּ in us = ב+1cp; consonants לנו/בנו)
    "בָּנוּ",  # in us — ב+1cp suffix (also catches they-built 3cp perf of בנה)
    "מֶנּוּ",  # from him/it — מִן+3ms suffix (after outer מ stripped from מִמֶּנּוּ)
    "מִמֶּנִּי",  # from me — מִן+1cs suffix
    "תַּחְתֶּנָּה",  # beneath her/it — תַּחַת+3fs suffix (consonants תחתנה)
    "תַּחְתֶּיהָ",  # beneath her — תַּחַת+3fs suffix variant (consonants תחתיה)
    "תַּחְתָּיו",  # beneath him — תַּחַת+3ms suffix (consonants תחתיו)
    "מִמֶּנָּה",  # from her — מִן+3fs suffix
)
HEBREW_PREPOSITIONS_CONST = tuple(constanants(w) for w in HEBREW_PREPOSITIONS)

__all__ = (
    "HebPreposition",
    "is_preposition",
)


@dataclass(frozen=True)
class HebPreposition:
    """Hebrew Preposition."""

    word: str
    word_constanants: str
    raw: str
    vav_consec: bool
    definite_article: bool
    preposition: str | None


def is_preposition(elements: CommonElements) -> HebPreposition | None:
    """Is the word a preposition."""
    if constanants(elements.word) not in HEBREW_PREPOSITIONS_CONST:
        return None

    return HebPreposition(
        preposition=elements.preposition,
        vav_consec=elements.vav_consec,
        definite_article=elements.definite_article,
        word=elements.word,
        word_constanants=constanants(elements.word),
        raw=elements.raw,
    )
