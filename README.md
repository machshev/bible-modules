# Bible Modules

[![ci](https://github.com/machshev/bible-modules/workflows/ci/badge.svg)](https://github.com/machshev/bible-modules/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://machshev.github.io/bible-modules/)
[![pypi version](https://img.shields.io/pypi/v/abm-tools.svg)](https://pypi.org/project/abm-tools/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/machshev/bible-modules)

Initially this project started out focusing on just the Aramaic Peshitta
modules. This is where the biggest gap was at the time. However while developing
[Haqor](https://github.com/machshev/haqor-core) it became apparent that the
existing Hebrew modules are also somewhat defficient in some ways. So this
project has now expanded to include all original language bible modules. As
well as generating a bespoke perpose built module and module format for `haqor`.

The idea is to provide everything from the source texts to the pre generated
bible modules themselves including the code to generate them. This means anyone
can review the generation process and make improvements as required.

None of this would be possible without the [source documents](#source-documents)
generously provided free to use for all. These scripts are therefore also
provided under the Apache 2.0 licence, as I've done very little work on top
of the many years of time and effort various people have spent compiling the
original information. If you need a different license for some reason then
please open an issue and let me know.

"freely ye have received, freely give." (Mat 10:8)

## Table of Contents

<!--TOC-->

- [Bible Modules](#bible-modules)
  - [Table of Contents](#table-of-contents)
  - [Pre-generated modules](#pre-generated-modules)
  - [Installing](#installing)
    - [Clone the repository](#clone-the-repository)
    - [Environment setup - the easy way](#environment-setup---the-easy-way)
    - [Environment setup](#environment-setup)
  - [Usage](#usage)
  - [Why produce Aramaic bible modules](#why-produce-aramaic-bible-modules)
  - [Source documents](#source-documents)
    - [Peshitta and SEDRA](#peshitta-and-sedra)
    - [UXLC](#uxlc)
  - [Available Bible Modules](#available-bible-modules)

<!--TOC-->

## Pre-generated modules

The bible modules are available pre generated in the `modules` dir of this repo.
At some point I'll try and get them released as part of a github release
artefact and perhaps even pushed to the various bible module registries
automatically as part of CI.

Until then just grab the files from `modules` dir. Github will provide a preview
of the Markdown versions see [Hebrew](https://github.com/machshev/bible-modules/blob/main/modules/md/hebrew.md)
and [Syriac](https://github.com/machshev/bible-modules/blob/main/modules/md/syriac.md).

## Installing

### Clone the repository

First clone the repository from github.

```bash
git clone git@github.com:machshev/bible-modules.git
cd bible-modules
```

### Environment setup - the easy way

If you have [nix](https://nix.dev/) and use [direnv](https://direnv.net/) then all
you need to do is `direnv allow .` and everything will be set up for you
automatically. You can skip the rest of this section.

If you don't have these setup or haven't heard of this and would like to experience the magic:

- Nix [zero-to-nix](https://zero-to-nix.com/start/install/).
- [direnv](https://direnv.net/)

(If you like these then maybe take a look at NixOS)

### Environment setup

First install [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a virtual environment. This is highly recommended as it keeps python
dependencies separate from your system Python. Otherwise you may end up updating
system python packages to incompatible versions and break other programs, or
doing an OS level package update (i.e. `apt` or `dnf`) will break this package
by changing dependency versions. By using a python virtual environment all
dependencies are kept separate.

```bash
uv venv
```

Install the required dependencies and this bm-tools package with a sync.

```bash
uv sync
```

The main part of the install is now complete. The above steps should not be
needed again.

Now you have a virtual environment you can activate it by sourcing the
activation script. This will have to be done every time you open a new shell as
it is essentially just setting environment variables to redirect python to the
virtual environment instead of the system python install.

```bash
. .venv/bin/activate
```

Finally done!
You should find the `bm` executable available in your terminal.

## Usage

To generate all the bible modules in one go.

```bash
bm gen all
```

For specific formats you can just generate the modules in the formats you want.
As an example this generates the HTML modules.

```bash
bm gen all -s html
```

For both HTML and Markdown

```bash
bm gen all -s html -s md
```

If you want more control over the generation process then take a look at
`bm gen bible --help`.

This project is still early stages and the number of formats is likely to
increase overtime. For the currently supported module formats see the pre
generated [modules](https://github.com/machshev/bible-modules/tree/main/modules).

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

### Peshitta and SEDRA

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

### UXLC

The UXLC is an XML version of the WLC and provided under a bespoke [license](https://tanach.us/License.html).
Please take a look at their site [tanach.us](https://tanach.us).

```
All biblical Hebrew text, in any format, may be viewed or copied without restriction.

Citation of the Tanach.us site as the source of the text is appreciated:


Unicode/XML Leningrad Codex: UXLC 2.3 (27.4),

Tanach.us Inc., West Redding, CT, USA, April 2025.

Documents with restrictions
```

### Sefaria

[Sefaria](https://www.sefaria.org/about) provides a large collection of jewish
texts, and related study resources. Two of the resources we make use of are the
the "DBD Dictionary" and "BDB Aramaic Dictionary" exported from the mongodb made
available in the public domain.

> For the Jewish people, our texts are our collective inheritance. They belong
> to everyone and we want them to be available to everyone, in the public domain
> or with free public licenses. Whether it’s copying a page of text for your
> classroom or [downloading our entire database](https://github.com/Sefaria/Sefaria-Export) for research and new projects,
> you’ll enjoy unfettered access to the canon.

We are grateful for this generosity.

## Available Bible Modules

This project aims to provide both OT, NT modules and also a lexicon module. For
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
