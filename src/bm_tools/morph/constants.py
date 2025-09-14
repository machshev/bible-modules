"""Constants."""

HEBREW_CONSANANTS = (
    "א",
    "ב",
    "ג",
    "ד",
    "ה",
    "ו",
    "ז",
    "ח",
    "ט",
    "י",
    "כ",
    "ך",  # Final Kaf
    "ל",
    "מ",
    "ם",  # Final Mem
    "נ",
    "ן",  # Final Nun
    "ס",
    "ע",
    "פ",
    "ף",  # Final Pe
    "צ",
    "ץ",  # Final Tzadi
    "ק",
    "ר",
    "שׁ",
    "ת",
)

HEBREW_GUTERALS_WEAK = (
    "א",
    "ע",
    "ר",
)

HEBREW_GUTERALS_HARSH = (
    "ה",
    "ח",
)

HEBREW_GUTERALS = HEBREW_GUTERALS_HARSH + HEBREW_GUTERALS_WEAK

HEBREW_INSEPARABLE_PREPOSITIONS = (
    "ב",
    "כ",
    "ל",
    "מ",
    # "ש",
)


HEBREW_PREPOSITIONS = (
    "אָשֵׁר",  # That
    "אֲשֶׁר",  # That
    "אַשֶׁר",  # That
    "אַשֻּׁר",  # That
    "כִּי",  # For
    "עַל",  # Upon
    "אֶל",  # To
    "לֹא",  # No/Not
    "אַל",  # No/Not
    "כָּל",  # All
    "עַד",  # Until
    "אִם",  # With
    "כָל",  # All
)

HEB_SHEVA = chr(0x05B0)
HEB_HATAF_SEGOL = chr(0x05B1)
HEB_HATAF_PATAH = chr(0x05B2)
HEB_HATAF_QAMATS = chr(0x05B3)

HEB_HIRIQ = chr(0x05B4)
HEB_TSERE = chr(0x05B5)
HEB_SEGOL = chr(0x05B6)
HEB_PATAH = chr(0x05B7)
HEB_QAMATS = chr(0x05B8)
HEB_QAMATS_QATAN = chr(0x05C7)
HEB_QUBUTS = chr(0x05BB)

HEB_HOLAM = chr(0x05B9)
HEB_HOLAM_HASER = chr(0x05BA)  # for Vav

HEB_DAGESH = chr(0x05BC)
HEB_MAPIQ = chr(0x05BC)

HEB_SHIN_DOT = chr(0x05C1)
HEB_SIN_DOT = chr(0x05C2)

HEBREW_VOWELS = (
    HEB_SHEVA,
    HEB_HATAF_SEGOL,
    HEB_HATAF_PATAH,
    HEB_HATAF_QAMATS,
    HEB_HIRIQ,
    HEB_TSERE,
    HEB_SEGOL,
    HEB_PATAH,
    HEB_QAMATS,
    HEB_QAMATS_QATAN,
    HEB_QUBUTS,
    HEB_HOLAM,
    HEB_HOLAM_HASER,
    HEB_DAGESH,
    HEB_MAPIQ,
    HEB_SHIN_DOT,
    HEB_SIN_DOT,
)

HEB_SUFFIX = (
    HEB_PATAH + "ה",  # perf.s.3.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_QAMATS,  # perf.s.2.m
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA,  # perf.s.2.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_HIRIQ + "י",  # perf.s.2.f
    "ו" + HEB_DAGESH,  # perf.pl.3.c
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA + "ם",  # perf.s.2.f
    HEB_SHEVA + "ת" + HEB_DAGESH + HEB_SHEVA + "ן",  # perf.s.2.f
    HEB_SHEVA + "נו" + HEB_DAGESH,  # perf.pl.1.c
    # Nouns
    HEB_HIRIQ + "י",  # to me
    "ו" + HEB_HOLAM,  # to him
    "ך" + HEB_QAMATS_QATAN,  # to you (s.2.m)
    HEB_PATAH + "י",  # my
    HEB_QAMATS + "י",  # my
    HEB_QAMATS_QATAN + "י",  # my
    HEB_TSERE + "י",  # of
    HEB_QAMATS + "ה",  # Her
    HEB_HIRIQ + "ים",  # Pl.m
    "ו" + HEB_HOLAM + "ת",  # Pl.f
    HEB_SEGOL + "ת",  # Pl.f
    HEB_HIRIQ + "ית",  # Pl.f
)

HEB_PREFIX = (
    "י" + HEB_SHEVA,  # y'
    "י" + HEB_HIRIQ,  # Yi
    "י" + HEB_PATAH,  # Ya
    "י" + HEB_QAMATS,  # Ya
    "י" + HEB_QAMATS_QATAN,  # Ya
    "י" + HEB_DAGESH + HEB_SHEVA,  # y'
    "י" + HEB_DAGESH + HEB_HIRIQ,  # Yi
    "י" + HEB_DAGESH + HEB_PATAH,  # Ya
    "ת" + HEB_HIRIQ,  # Ti
    "א" + HEB_SEGOL,  # 'e
)
