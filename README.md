# Aramaic Bible Modules

Provides the SEDRA 3 source files and the Python based tools to generate Aramaic
bible software modules in common formats... for example SWORD, MySWORD, E-SWORD modules.

## Why produce Aramaic bible modules

This is the reason that I personally want free access to good quality Peshitta
texts linked to a good quality Aramaic lexicon. It will allow me to study the NT
in Aramaic in the same way I can the OT Hebrew and NT Greek texts.

It's clear that Jesus spoke Aramaic, and that the whole eastern region at the
time used one form of Aramaic or another. Josephus describes Greek and a foreign
and an unknown tongue, showing that Greek was not widely known or understood by
the Jews in the land of Israel at the time of Jesus. Hellenistic forces were
actively and passionately fought against.

Examples of Aramaic used at the time are Talmudic Aramaic, and Galilean Aramaic.
There are verses in the NT Greek texts that preserve Aramaic speech, for example
"Talitha cum" (Mark 5:41) and "Eli Eli Lema Sabachthani" (Matt 27:46) amongst
others. Suggesting that Jesus taught using Aramaic.

We also know that while Jesus' disciples were centred in the Galilee throughout
his ministry, and then in Jerusalem immediately after his death and
resurrection. The Syrian capital Antioch was the first place the disciples were
called Christians.

    Acts 11:26 And when he had found him, he brought him unto Antioch. And it came
    to pass, that a whole year they assembled themselves with the church, and taught
    much people. And the disciples were called Christians first in Antioch.

Antioch was a Greek city founded by Seleucus one of the four generals of
Alexander the Great. It contained a large Jewish population and one of the
centres of Hellenistic Judaism in the region. As such it was the perfect
location for both the Greek and Aramaic texts of the NT to originate... Greek
for the West and Aramaic for the East.

This is not the place to try and persuade people that Aramaic or Greek texts are
the "original". I suspect the truth is a little more complicated, and both were
divinely arranged to come about (inspired). Both to make the gospel available in
the main language of the East and the West.

From my experience so far, when it comes to English translations of both texts
there is little difference and certainly no major doctrinal differences. However
translation is never perfect, it's simply not possible to translate the richness
of some languages into others... capturing all the cultural subtleties and plays
on words. For those who can, I'd recommend learning to read the original
languages.

So what's the value of the Peshitta? It may not be the same dialect as the
original Aramaic spoken by Jesus and his disciples, however it's still Aramaic
and more capable of capturing the subtleties of the Hebrew/Aramaic thought we
know Jesus taught in. There are several examples of two variant readings in the
Greek texts being perfectly valid translations of the one Aramaic word found in
the Peshitta.

There are also a number of occasions where I've found allusions back to Hebrew
OT passages via Aramaic words which share the same root as Hebrew words. Too
many to be coincidence in my opinion. This is one of the unique features of the
bible, especially the Hebrew; the sheer number of internal references and word
link allusions is in my opinion beyond Human capability. The Peshitta seems to
follow that pattern within itself and also beyond itself into the Hebrew as one
united whole. The Greek NT reflects this within itself, as it would be expected
to do being either directly inspired or divinely arranged translation of an
inspired Aramaic text (I'm not absolutely certain which one). However it doesn't
have the same capacity for the same kind of links between OT and NT, as Greek
and Hebrew are very different languages and very different ways of thinking.

Individuals will ultimately have to make their own mind up. The aim of this
project is to make these texts more available than they currently are.

## Source documents

The Peshitta NT text provided is the BFBS version that comes with the SEDRA 3
project distribution, a crowd sourced Syriac Lexicon project. These files are
made freely available from [Beth Mardutho](https://sedra.bethmardutho.org/).
Further details of the SEDRA project can be found on this website, as well as
the following publication.

    G. Kiraz, `Automatic Concordance Generation of Syriac Texts'. 
    In VI Symposium Syriacum 1992, ed. R. Lavenant, Orientalia Christiana
    Analecta 247, Rome, 1994.

SEDRA 3 was the last release in downloadable file format. SEDRA 4 is available
as a living online DB that is accessible under Apache 2.0 licence (hence the
reason this project is also using that licence) via a JSON API
[OpenAPI](https://sedra.bethmardutho.org/about/openapi#tag/API).

## Modules
This project aims to provide both NT text modules and also a lexicon module. For
the texts, it is intended that at least two versions be produced. The first
using Unicode Hebrew consonants and pointing for those who are already familiar
with Hebrew but not yet the Aramaic script, as a means of making the text more
accessible to bible students. The second using Unicode Aramaic consonants and
vowel pointing for those familiar with the Aramaic script.

The lexicon module should be shared by any bible modules provided and use the
SEDRA numbers as references (of the form SXXXX paralleling the HXXXX and GXXXX
Hebrew and Greek strongs numbers normally used as references). This may also
require updates to bible software projects so they can use SEDRA numbers as they
currently do Strongs numbers.
