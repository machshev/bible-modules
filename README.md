# Bible Modules

[![ci](https://github.com/machshev/bible-modules/workflows/ci/badge.svg)](https://github.com/machshev/bible-modules/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://machshev.github.io/bible-modules/)
[![pypi version](https://img.shields.io/pypi/v/abm-tools.svg)](https://pypi.org/project/abm-tools/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/machshev/bible-modules)

Provides the SEDRA 3 source files and the Python based tools to generate Aramaic
bible software modules in common formats... for example SWORD, MySWORD, E-SWORD
modules. Rather than just providing the generated modules (which I'm hoping will
be available from the normal module sites), I'd like to share the scripts used
to generate them. That way if someone finds, as I have, that their preferred
bible software doesn't have a module available... then you can use these scripts
as a starting point to generate one.

None of this would be possible without the [source documents](#source-documents)
generously provided free to use for all. These scripts are therefore also
provided under the same Apache 2.0 licence, as I've done very little work on top
of the many years of time and effort various people have spent compiling the
original information.

"freely ye have received, freely give." (Mat 10:8)

## Table of Contents

<!--TOC-->

- [Bible Modules](#bible-modules)
  - [Table of Contents](#table-of-contents)
  - [Installing](#installing)
    - [Clone the repository](#clone-the-repository)
    - [From package](#from-package)
  - [Usage](#usage)
  - [Why produce Aramaic bible modules](#why-produce-bible-modules)
  - [Source documents](#source-documents)
  - [Available Bible Modules](#available-bible-modules)

<!--TOC-->

## Installing

You will need a version of Python 3 installed to run these scripts. At the
moment I've not got access to pypi due to an issue with 2FA and a misshap with
my phone a few months back. However the plan is to release a package on pypi to
make it easier to install. For the moment however installing from source is the
only option.

### Clone the repository

First clone the repository from github.

```bash
git clone git@github.com:machshev/bible-modules.git
cd bible-modules
```

Install [pdm](https://pdm-project.org/en/latest/), the "modern python packaging
and dependency manager", this allows us to install the versions pinned in the
lockfile for consistent result. We use `pdm` to manage dependencies as well as
create a virtual environment to run the scripts from with all the required
dependencies.

```bash
pip install pipx
pipx install pdm
pdm install
```

### From package

_Note:_ Not available right now.

With `pip`:

```bash
pip install abm-tools
```

With [`pipx`](https://github.com/pipxproject/pipx):

```bash
python3.8 -m pip install --user pipx
pipx install abm-tools
```

## Usage

To generate the bible modules individually use the `bm_tools gen bible`
command. There is help available via `--help` flag to see what formats are
currently available.

For example, this command will generate the html format using the hebrew unicode
characters rather than the default syriac unicode characters.

```bash
abm-tools gen bible --alphabet hebrew --format html abm_hebrew ./output
```

This project is still early stages. However it's possible to generate some
"modules"... right now that is just a Markdown or HTML export of the whole of
the Peshitta. It's possible to select the alphabet used for this, SEDRA3 uses
latin characters in place of the Syriac characters. These Latin characters are
transformed to Unicode, and optionally either Syriac or Hebrew. The mappings
seem to be correct as manually verified for the first few verses of Matthew,
however I wouldn't be supprised if there were pointing marks that are not
correct and those will be corrected over time with more manual checking.

There is a Makefile that will auto generate the full set of available modules,
and alphabet combinations. The output is generated in the `output` directory.

```bash
make modules
```

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

G. Kiraz, `Automatic Concordance Generation of Syriac Texts'. In VI Symposium
Syriacum 1992, ed. R. Lavenant, Orientalia Christiana Analecta 247, Rome, 1994.

SEDRA 3 was the last release in downloadable file format. SEDRA 4 is available
as a living online DB that is accessible under Apache 2.0 licence (hence the
reason this project is also using that licence) via a JSON API
[OpenAPI](https://sedra.bethmardutho.org/about/openapi#tag/API).

## Available Bible Modules

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
