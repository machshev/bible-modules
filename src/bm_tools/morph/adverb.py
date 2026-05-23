"""Parse Adverbs."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebAdverb",
    "is_adverb",
)

HEB_ADVERB = (
    # Participle
    "גַּם",  # Also, even
    "אַף",  # Also/even
    "אַךְ",  # Surly
    "רַק",  # Only
    "הִנֵּה",  # Behold
    "נָא",  # Please now
    "כֹּה",  # So
    "עַד",  # Until
    "עוֹד",  # further
    "כֵן",  # Yes / it is so
    "אַחֲרֵי",  # After
    "יְהִי",  # let there be / may it be (jussive of היה)
    "עַתָּה",  # now
    "אוֹ",  # or (conjunction)
    "דֵּי",  # enough / that (Aramaic particle; also כְּדֵי, מִדֵּי)
    "הִנּוֹ",  # behold him / here he is (הִנֵּה + 3ms suffix; consonants הנו)
    "מַעַן",  # for the sake of / in order that (typically as לְמַעַן after ל strip)
    "הִנְנִי",  # behold me / here I am (הִנֵּה + 1cs suffix; consonants הנני)
    "הֲלוֹא",  # is it not? / surely (rhetorical question particle; consonants הלוא)
    "פֶּן",  # lest / so that not (negative purpose conjunction; consonants פן)
    "יֵשׁ",  # there is / there are (existential particle; consonants יש)
    "טֶרֶם",  # before / ere (temporal adverb; consonants טרם)
    "מוֹ",  # indeed/truly / from them (archaic particle; consonants מו)
    "מְעַט",  # a little / few (adverb; consonants מעט)
    "מָה",  # what / how (interrogative/exclamatory particle; consonants מה)
    "רִאשֹׁנָה",  # at first / formerly (adverb; consonants ראשנה)
    "שְׁלֹשָׁה",  # three (numeral; consonants שלשה)
    "שְׁמוֹנֶה",  # eight (numeral; consonants שמונה)
    "שְׁמוֹנִים",  # eighty (numeral; consonants שמונים)
    "מִחוּץ",  # outside / from outside (compound preposition; consonants מחוץ)
    "לְפָנִים",  # formerly / before (temporal adverb; consonants לפנים)
    "בְּטֶרֶם",  # before / ere (compound with ב; consonants בטרם)
    "מַדּוּעַ",  # why? (interrogative particle; consonants מדוע)
    "אֵין",  # there is not / no (negative existential; consonants אין)
    "אַיִן",  # there is not / where? (negative existential/interrogative; consonants איין/אין)  # noqa: E501
    "אֵינֶנּוּ",  # he is not (אין + 3ms suffix; consonants איננו)
    "אֵינֶנָּה",  # she is not (אין + 3fs suffix; consonants איננה)
    "אֵינֶנִּי",  # I am not (אין + 1cs suffix; consonants איינני)
    "אֵינְכֶם",  # you (mp) are not (אין + 2mp suffix; consonants אינכם)
    "אֵינְכֶן",  # you (fp) are not (אין + 2fp suffix; consonants אינכן)
    "אֵינָם",  # they are not (אין + 3mp suffix; consonants אינם)
    "אֵינָן",  # they (fp) are not (אין + 3fp suffix; consonants אינן)
    "פִּתְאֹם",  # suddenly (consonants פתאם)
    "לָמָּה",  # why? (interrogative; consonants למה)
    "אֵיפֹה",  # where? (interrogative; consonants איפה)
    "אֵיכָה",  # how? / alas! (interrogative/lament; consonants איכה)
    "בִּלְתִּי",  # not / without (negative particle; consonants בלתי)
    "לֹא",  # not (negative particle; consonants לא)
    "אַל",  # do not (negative particle; consonants אל)
)
HEB_ADVERB_CONST = tuple(constanants(w) for w in HEB_ADVERB)


@dataclass(frozen=True)
class HebAdverb:
    """Hebrew Adverb."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    vav_consec: bool
    raw: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel


def is_adverb(elements: CommonElements) -> HebAdverb | None:
    """Is the word a Adverb?"""
    if constanants(elements.word) not in HEB_ADVERB_CONST:
        return None

    gender = ""
    number = ""

    return HebAdverb(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        vav_consec=elements.vav_consec,
        gender=gender,
        number=number,
        word_constanants=constanants(elements.word),
        word=elements.word,
        raw=elements.raw,
    )
