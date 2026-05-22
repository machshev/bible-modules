"""Parse Nouns."""

from dataclasses import dataclass

from bm_tools.morph.helpers import constanants
from bm_tools.morph.models import CommonElements

__all__ = (
    "HebNoun",
    "is_noun",
)

# TODO: this needs to move to a separate file
COMMON_NOUNS = (
    "יִשְׂרָאֵל",
    "מֶלֶךְ",
    "אֶרֶץ",
    "בֶּן",
    "בְנֵי",  # construct plural / bound forms of בן (sons of)
    "בַיִת",
    "עַם",
    "אִישׁ",
    "יוֹם",
    "יָמִים",  # plural of יוֹם (days)
    "דִּבֶּר",
    "פְּנֵי",
    "אֱלֹהִים",
    "אֱלֹהָי",  # my God (אֱלֹהִים + 1cs suffix)
    "שָׁם",
    "דּוֹד",
    "מִצְרִים",
    "עִיר",
    "אֲדֹנָי",
    "אָדָם",
    "יַד",
    "יְרוּשָׁלִַם",
    "שָׁנָה",
    "כֹהֵן",
    "שָׁאוּל",
    "מָיִם",
    "דֶּרֶךְ",
    "גוֹיִם",
    "אִשָּׁה",
    "שָׁמַיִם",
    "הַר",
    "זָהָב",
    "אוֹת",
    "קֹדֶשׁ",
    "חֶרֶב",
    "רֹב",
    "אֵשׁ",
    "יַעֲקֹב",
    "קוֹל",
    "יְהוּדָה",
    "מֹשֶׁה",
    "אֶחָד",
    "טוֹב",
    "עוֹלָם",
    "עֶשְׂרִים",
    "אֶלֶף",
    "מִזְבֵּחַ",
    "מָקוֹם",
    "רוּחַ",
    "רָע",
    "רֹאשׁ",
    "פַרְעֹה",
    "שַׁעַר",
    "שָׂדֶה",
    "אֹמֶר",  # utterance / word
    "נְתָן",  # Nathan (proper name; also נְתַן variant)
    "נְאֻם",  # oracle of / utterance of (prophetic formula נְאֻם יְהוָה)
    "עֵינֵי",  # eyes of (construct plural / suffix forms of עַיִן)
    "אֱלֹהֶיךָ",  # your God (אֱלֹהִים + 2ms/2fs suffix; consonants אלהיך)
    "בָּא",  # coming / one who comes (Qal ptcp/perf of בוא; hollow verb, 2 cons: בא)
    "דִּבְרֵי",  # words of (construct plural of דָּבָר; consonants דברי)
    "עֵלִי",  # Eli (proper name; priest in Samuel; consonants עלי)
    "שָׁנִים",  # years (plural of שָׁנָה) / two (שְׁנַיִם dual); consonants שנים
    "רֵעֶה",  # friend / neighbor / another (consonants רעה; also רֵעָה, רְעֵה)
    "עֵשָׂו",  # Esau (proper name; also catches עָשׂוּ/עֲשׂוּ 3cp perf of עשה)
    "עָלֶה",  # leaf / foliage (consonants עלה; also catches verb forms עָלָה go up)
    "צִבְאוֹת",  # armies / hosts (as in יְהוָה צְבָאוֹת Lord of Hosts; consonants צבאות)
    "שֵׁנִי",  # second (ordinal numeral; consonants שני; also שְׁנֵי two of)
    "עֶשֶׂר",  # ten / tithe (consonants עשר; also עַשֵּׂר tithe, עֹשֶׁר wealth)
    "יָם",  # sea (consonants ים; also construct form יַם)
    "דָּוִיד",  # David (proper name; consonants דויד)
    "גָּדוֹל",  # great (adjective; consonants גדול; all inflections share root)
    "עַמִּי",  # my people (עַם+1cs; consonants עמי; also עִמִּי with me = עִם+1cs)
    "הָיוּ",  # they were (Qal perf 3cp of היה; consonants היו; also הֱיוּ imperative pl)
    "פִּי",  # my mouth (construct of פֶּה; consonants פי; also catches כַּפַּי my palms)
    "כֹּהֲנִים",  # priests (plural of כֹּהֵן; consonants כהנים)
    "חֵם",  # residual of לֶחֶם (bread) after ל incorrectly stripped as preposition; cons חם  # noqa: E501
    "אֲנָשִׁים",  # men / people (plural of אִישׁ; consonants אנשים)
    "מִלְחָמָה",  # war / battle (consonants מלחמה)
    "תּוֹךְ",  # midst / within (consonants תוך; as in בְּתוֹךְ in the midst of)
    "הֶבֶל",  # Abel (proper name) / vanity / breath (consonants הבל)
    "בָּבֶל",  # Babylon (proper name; consonants בבל)
    "יָדוֹ",  # his hand (יָד+3ms suffix; consonants ידו)
    "אָחִיו",  # his brother (אָח+3ms suffix; consonants אחיו)
    "מִדְבָּר",  # wilderness / desert (consonants מדבר; also מְדַבֵּר Piel ptcp speaking)
    "שְׁלֹמֹה",  # Solomon (proper name; consonants שלמה; also שַׂלְמָה garment/cloak)
    "עֲשׂוֹת",  # to do / doing (Qal inf construct of עשה; consonants עשות)
    "סָבִיב",  # around / surrounding (consonants סביב; also סְבִיבוֹת round about)
    "הַלְוִיִּם",  # the Levites (article+plural; consonants הלוים — article not stripped)
    "לַלְוִיִּם",  # to the Levites (ל+article+Levites; consonants ללוים)
    "בַּלְוִיִּם",  # among the Levites (ב+article+Levites; consonants בלוים)
    "חֹדֶשׁ",  # month / new moon (consonants חדש; also חַדֵּשׁ renew/new)
    "לֵב",  # heart (consonants לב; also לֶב construct form)
    "מַעַן",  # sake / purpose (as in לְמַעַן for the sake of; consonants מען)
    "בֹּקֶר",  # morning (consonants בקר)
    "בַּת",  # daughter (consonants בת; also construct form בַת)
    "פָּנָיו",  # his face / before him (פָּנִים+3ms suffix; consonants פניו)
    "עֵת",  # time / season (consonants עת; also עֶת variant)
    "עֵבֶר",  # side / beyond / across (consonants עבר; also עֲבֻר for the sake of)
    "פְּלִשְׁתִּים",  # Philistines (consonants פלשתים)
    "יוֹסֵף",  # Joseph (proper name; consonants יוסף; also וַיּוֹסֶף he continued)
    "נָתַתִּי",  # I gave (Qal perf 1cs of נתן; pe-nun contracted; consonants נתתי)
)
COMMON_NOUNS_CONST = tuple(constanants(w) for w in COMMON_NOUNS)


@dataclass(frozen=True)
class HebNoun:
    """Hebrew Noun."""

    preposition: str | None
    definite_article: bool
    word: str
    word_constanants: str
    vav_consec: bool
    raw: str
    gender: str  # i.e. (m)asculin, (f)eminin, and (n)uteral
    number: str  # i.e. (s)ingular. (p)lural, and (d)uel


def is_noun(elements: CommonElements) -> HebNoun | None:
    """Is the word a Noun?"""
    if constanants(elements.word) not in COMMON_NOUNS_CONST:
        return None

    gender = ""
    number = ""

    return HebNoun(
        preposition=elements.preposition,
        definite_article=elements.definite_article,
        vav_consec=elements.vav_consec,
        gender=gender,
        number=number,
        word_constanants=constanants(elements.word),
        word=elements.word,
        raw=elements.raw,
    )
