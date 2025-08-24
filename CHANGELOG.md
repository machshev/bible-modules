# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [2.1.0](https://github.com/machshev/bible-modules/releases/tag/2.1.0) - 2025-08-24

<small>[Compare with 2.0.0](https://github.com/machshev/bible-modules/compare/2.0.0...2.1.0)</small>

### Features

- more accurate inseparable preposition parsing ([6166a44](https://github.com/machshev/bible-modules/commit/6166a44ad1f5264f7ff894ea7cc155335d2e9e13) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- more accurate definite article parsing ([55d9b49](https://github.com/machshev/bible-modules/commit/55d9b490e8f78b27e94183d2e313f3cee35bb247) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- expand prefix and suffix patturns ([ad368e0](https://github.com/machshev/bible-modules/commit/ad368e074ad17f825d01b37cfb69396f474375a5) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- vav consecutive and definite article ([1f2fcc4](https://github.com/machshev/bible-modules/commit/1f2fcc47fa43304782058112116a1eeccf29b2ce) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add DBD source texts ([e26acaf](https://github.com/machshev/bible-modules/commit/e26acaf6ec7914182827fab53529d30a3bdea1e0) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- strip off prefix and suffix ([60988fb](https://github.com/machshev/bible-modules/commit/60988fb89e33dbad50afc4c836fc9a55ff67c3cd) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add back in vowel stripping on parsed words ([c78deb9](https://github.com/machshev/bible-modules/commit/c78deb9707627bab9e121c0bccc4ac20ef2c621f) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- use seporate words and count DB tables ([3229e71](https://github.com/machshev/bible-modules/commit/3229e71575913e2779934025fa926fa6c32ce9a3) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add simple morphology evaluation ([a1ed901](https://github.com/machshev/bible-modules/commit/a1ed901fe386e17b343344291b0a25aba4535495) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add simple word count ([873ed35](https://github.com/machshev/bible-modules/commit/873ed35fb8be717d9bc8459bd2cc62a4f1f211a4) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add simplistic word count ([0d60b9e](https://github.com/machshev/bible-modules/commit/0d60b9edc1b470f5e194dada65f074f667fa96fe) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add the OT to all bible modules ([70fc223](https://github.com/machshev/bible-modules/commit/70fc223d1762fe5bd27306f29e792cc37b4bb330) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>

### Bug Fixes

- treat uxlc x tags correctly ([265518d](https://github.com/machshev/bible-modules/commit/265518de6b4c9b1cb94321db8cf071d0b314832a) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- preserve existing modules on regen. ([c14b1d2](https://github.com/machshev/bible-modules/commit/c14b1d2cf8474eb4cea4354a187c2d3cbad6e5f1) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- couple of off by one errors ([238fbf0](https://github.com/machshev/bible-modules/commit/238fbf0bad6e368ec6cd5ecf174fe32fec6316d1) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>

## [2.0.0](https://github.com/machshev/bible-modules/releases/tag/2.0.0) - 2025-06-08

<small>[Compare with 1.2.0](https://github.com/machshev/bible-modules/compare/1.2.0...2.0.0)</small>

### Build

- nix-shell ([f3cdceb](https://github.com/machshev/bible-modules/commit/f3cdceb4d46e8affe2b246c54713b57d1124ccb2) by David James McCorrie).

### Dependencies

- add ipython/ipdb to the devshell and use ipdb for breakpoints ([63c7d9c](https://github.com/machshev/bible-modules/commit/63c7d9c63696b981d066f3459b263ef586dffce1) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>

### Features

- new command to easily generate all modules ([48cac8c](https://github.com/machshev/bible-modules/commit/48cac8c5c229852e0cb0bb2e9fcfc6fc9f871796) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- parse all UXLC bible books ([dbdc03a](https://github.com/machshev/bible-modules/commit/dbdc03a46607c751155f85231c6b50d09e715f4d) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- parse UXLC bible book ([42d9d00](https://github.com/machshev/bible-modules/commit/42d9d0007600a32f7f948cb9463a1df144758dcc) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- Initial support for Haqor bible module ([b9ed845](https://github.com/machshev/bible-modules/commit/b9ed8452e2fe6505f95deb8e33736ba3f88be465) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add UXLC src ([075e93a](https://github.com/machshev/bible-modules/commit/075e93a90be75c2a3555e25ac89f9d7e8f59eced) by David James McCorrie).
- simple osis support with structure and word lemma ([e6e2ba5](https://github.com/machshev/bible-modules/commit/e6e2ba54e3d6e0a9c5be7895d0f456010ea64d76) by David James McCorrie).

### Bug Fixes

- duty scripts fix issues ([86126fd](https://github.com/machshev/bible-modules/commit/86126fd962c8aa281cb80412a60b744aa3fc25ba) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- remove safety check from the CI config as it requires registration ([63b25e7](https://github.com/machshev/bible-modules/commit/63b25e7bdff5bd957d92fd41cfdab337fcccd7ce) by David James McCorrie).
- use Safety 3.2.0 scanning /home/david/base/bible-modules 2024-06-04 10:30:08 UTC ([8534ad6](https://github.com/machshev/bible-modules/commit/8534ad6b49a38a12ac443facda4f1683d2c54630) by David James McCorrie).

### Code Refactoring

- change main cli name bm_tools -> bm as it's easier to type ([636f735](https://github.com/machshev/bible-modules/commit/636f735eba7bb5fa6b08a39bf108a6ae7caa1452) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- tidy up src texts and small fixes ([7e6b7c1](https://github.com/machshev/bible-modules/commit/7e6b7c1658ddd967029aaa6b1cc31503c3ff7d9a) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- Convert to UV and add flake ([9d0ece3](https://github.com/machshev/bible-modules/commit/9d0ece363bb5bafbe1f7b7d14783c7ef5a13c61d) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- rename from aramaic-bible-modules to bible-modules to broaden the project scope ([5d95af2](https://github.com/machshev/bible-modules/commit/5d95af24869ef515601a5c9c3b7fbd3b7cdaf8c5) by David James McCorrie).

## [1.2.0](https://github.com/machshev/bible-modules/releases/tag/1.2.0) - 2024-04-12

<small>[Compare with first commit](https://github.com/machshev/bible-modules/compare/a5f4d34d7f9d50e88fa6188df613db95ea7741ea...1.2.0)</small>

### Build

- significant refactor of the build scripts using copier-pdm template ([78ad8e3](https://github.com/machshev/bible-modules/commit/78ad8e388ac84e4bf3f56286ffa09126c0363cf0) by David James McCorrie).
- add auto-changelog ([71d5ecb](https://github.com/machshev/bible-modules/commit/71d5ecb894da82b38c0279ad9f37a5e6140c0333) by David James McCorrie).
- update the pdm lock with latest versions ([e578bca](https://github.com/machshev/bible-modules/commit/e578bcaa03f9d493cbfca03dfbff2cea34056509) by David James McCorrie).
- update dependancy versions ([25901b6](https://github.com/machshev/bible-modules/commit/25901b6a4231172e0fa3c28d71f702bc50de73ea) by David James McCorrie).
- fixed the pyproject.toml dep versions imported from poetry ([6f0a6d2](https://github.com/machshev/bible-modules/commit/6f0a6d2cb14eda2f24c36524220d153b4ffe8dba) by David James McCorrie).
- add .pdm-python to .gitignore ([f6e7981](https://github.com/machshev/bible-modules/commit/f6e79813f5df38a99cd09260f69c365415c4c1d6) by David James McCorrie).
- migrate from poetry to pdm ([6b1a92d](https://github.com/machshev/bible-modules/commit/6b1a92d18fda2a53431a234db7cb10b3ddeb8193) by David James McCorrie).

### Features

- add support for final forms, and improve the hebrew translit mappings ([e4407d6](https://github.com/machshev/bible-modules/commit/e4407d6ab88255182028f9156dee9fbf92016a1b) by David James McCorrie).
- add initial support for vpl and osis ([7e901d6](https://github.com/machshev/bible-modules/commit/7e901d693f1b70da1f300722c405fbd8146e8f1d) by David James McCorrie).
- proper syriac font in generated HTML ([021e3c3](https://github.com/machshev/bible-modules/commit/021e3c34420bb5f466c21298b005bb7dafa4a10f) by David James McCorrie).
- add support for HTML bible module generation as well as Markdown ([c047d89](https://github.com/machshev/bible-modules/commit/c047d89cb6c0f9fd9dc7d668feed6c36f5c25fa6) by David James McCorrie).
- generate bible text using either Hebrew/syriac unicode alphabets ([7ca9a3d](https://github.com/machshev/bible-modules/commit/7ca9a3d4eb79902c6564960466a7aec8848ca4f0) by David James McCorrie).

### Bug Fixes

- tests ([a769fd1](https://github.com/machshev/bible-modules/commit/a769fd15d5dd4d373675e3c6c70986315d5a99ec) by David James McCorrie).
- ci only use 3.12 ([8e16abf](https://github.com/machshev/bible-modules/commit/8e16abfb0046a6634e5147423d92cf5f41c7abd9) by David James McCorrie).
- add build all modules back to makefile, docs updated ([a412d8d](https://github.com/machshev/bible-modules/commit/a412d8d195cc57be39569d88b628d480473311a8) by David James McCorrie).
- github url ([70c8fc5](https://github.com/machshev/bible-modules/commit/70c8fc525f080faa6ef7e01436c155da0b8bbd71) by David James McCorrie).

### Code Refactoring

- start to add some more meaningfull structure ([bb0b0b4](https://github.com/machshev/bible-modules/commit/bb0b0b45bb14d4bed041ba3af95c0f1e1a336e2b) by David James McCorrie).

## [1.3.0](https://github.com/machshev/bible-modules/releases/tag/1.3.0) - 2025-06-08

<small>[Compare with 1.2.0](https://github.com/machshev/bible-modules/compare/1.2.0...1.3.0)</small>

### Build

- nix-shell ([f3cdceb](https://github.com/machshev/bible-modules/commit/f3cdceb4d46e8affe2b246c54713b57d1124ccb2) by David James McCorrie).

### Dependencies

- add ipython/ipdb to the devshell and use ipdb for breakpoints ([63c7d9c](https://github.com/machshev/bible-modules/commit/63c7d9c63696b981d066f3459b263ef586dffce1) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>

### Features

- new command to easily generate all modules ([48cac8c](https://github.com/machshev/bible-modules/commit/48cac8c5c229852e0cb0bb2e9fcfc6fc9f871796) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- parse all UXLC bible books ([dbdc03a](https://github.com/machshev/bible-modules/commit/dbdc03a46607c751155f85231c6b50d09e715f4d) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- parse UXLC bible book ([42d9d00](https://github.com/machshev/bible-modules/commit/42d9d0007600a32f7f948cb9463a1df144758dcc) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- Initial support for Haqor bible module ([b9ed845](https://github.com/machshev/bible-modules/commit/b9ed8452e2fe6505f95deb8e33736ba3f88be465) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- add UXLC src ([075e93a](https://github.com/machshev/bible-modules/commit/075e93a90be75c2a3555e25ac89f9d7e8f59eced) by David James McCorrie).
- simple osis support with structure and word lemma ([e6e2ba5](https://github.com/machshev/bible-modules/commit/e6e2ba54e3d6e0a9c5be7895d0f456010ea64d76) by David James McCorrie).

### Bug Fixes

- duty scripts fix issues ([86126fd](https://github.com/machshev/bible-modules/commit/86126fd962c8aa281cb80412a60b744aa3fc25ba) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- remove safety check from the CI config as it requires registration ([63b25e7](https://github.com/machshev/bible-modules/commit/63b25e7bdff5bd957d92fd41cfdab337fcccd7ce) by David James McCorrie).
- use Safety 3.2.0 scanning /home/david/base/bible-modules 2024-06-04 10:30:08 UTC ([8534ad6](https://github.com/machshev/bible-modules/commit/8534ad6b49a38a12ac443facda4f1683d2c54630) by David James McCorrie).

### Code Refactoring

- change main cli name bm_tools -> bm as it's easier to type ([636f735](https://github.com/machshev/bible-modules/commit/636f735eba7bb5fa6b08a39bf108a6ae7caa1452) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- tidy up src texts and small fixes ([7e6b7c1](https://github.com/machshev/bible-modules/commit/7e6b7c1658ddd967029aaa6b1cc31503c3ff7d9a) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- Convert to UV and add flake ([9d0ece3](https://github.com/machshev/bible-modules/commit/9d0ece363bb5bafbe1f7b7d14783c7ef5a13c61d) by David James McCorrie). Signed-off-by: David James McCorrie <djmccorrie@gmail.com>
- rename from aramaic-bible-modules to bible-modules to broaden the project scope ([5d95af2](https://github.com/machshev/bible-modules/commit/5d95af24869ef515601a5c9c3b7fbd3b7cdaf8c5) by David James McCorrie).

## [1.2.0](https://github.com/machshev/bible-modules/releases/tag/1.2.0) - 2024-04-12

<small>[Compare with first commit](https://github.com/machshev/bible-modules/compare/a5f4d34d7f9d50e88fa6188df613db95ea7741ea...1.2.0)</small>

### Build

- significant refactor of the build scripts using copier-pdm template ([78ad8e3](https://github.com/machshev/bible-modules/commit/78ad8e388ac84e4bf3f56286ffa09126c0363cf0) by David James McCorrie).
- add auto-changelog ([71d5ecb](https://github.com/machshev/bible-modules/commit/71d5ecb894da82b38c0279ad9f37a5e6140c0333) by David James McCorrie).
- update the pdm lock with latest versions ([e578bca](https://github.com/machshev/bible-modules/commit/e578bcaa03f9d493cbfca03dfbff2cea34056509) by David James McCorrie).
- update dependancy versions ([25901b6](https://github.com/machshev/bible-modules/commit/25901b6a4231172e0fa3c28d71f702bc50de73ea) by David James McCorrie).
- fixed the pyproject.toml dep versions imported from poetry ([6f0a6d2](https://github.com/machshev/bible-modules/commit/6f0a6d2cb14eda2f24c36524220d153b4ffe8dba) by David James McCorrie).
- add .pdm-python to .gitignore ([f6e7981](https://github.com/machshev/bible-modules/commit/f6e79813f5df38a99cd09260f69c365415c4c1d6) by David James McCorrie).
- migrate from poetry to pdm ([6b1a92d](https://github.com/machshev/bible-modules/commit/6b1a92d18fda2a53431a234db7cb10b3ddeb8193) by David James McCorrie).

### Features

- add support for final forms, and improve the hebrew translit mappings ([e4407d6](https://github.com/machshev/bible-modules/commit/e4407d6ab88255182028f9156dee9fbf92016a1b) by David James McCorrie).
- add initial support for vpl and osis ([7e901d6](https://github.com/machshev/bible-modules/commit/7e901d693f1b70da1f300722c405fbd8146e8f1d) by David James McCorrie).
- proper syriac font in generated HTML ([021e3c3](https://github.com/machshev/bible-modules/commit/021e3c34420bb5f466c21298b005bb7dafa4a10f) by David James McCorrie).
- add support for HTML bible module generation as well as Markdown ([c047d89](https://github.com/machshev/bible-modules/commit/c047d89cb6c0f9fd9dc7d668feed6c36f5c25fa6) by David James McCorrie).
- generate bible text using either Hebrew/syriac unicode alphabets ([7ca9a3d](https://github.com/machshev/bible-modules/commit/7ca9a3d4eb79902c6564960466a7aec8848ca4f0) by David James McCorrie).

### Bug Fixes

- tests ([a769fd1](https://github.com/machshev/bible-modules/commit/a769fd15d5dd4d373675e3c6c70986315d5a99ec) by David James McCorrie).
- ci only use 3.12 ([8e16abf](https://github.com/machshev/bible-modules/commit/8e16abfb0046a6634e5147423d92cf5f41c7abd9) by David James McCorrie).
- add build all modules back to makefile, docs updated ([a412d8d](https://github.com/machshev/bible-modules/commit/a412d8d195cc57be39569d88b628d480473311a8) by David James McCorrie).
- github url ([70c8fc5](https://github.com/machshev/bible-modules/commit/70c8fc525f080faa6ef7e01436c155da0b8bbd71) by David James McCorrie).

### Code Refactoring

- start to add some more meaningfull structure ([bb0b0b4](https://github.com/machshev/bible-modules/commit/bb0b0b45bb14d4bed041ba3af95c0f1e1a336e2b) by David James McCorrie).

## [1.2.1](https://github.com/machshev/aramaic-bible-modules/releases/tag/1.2.1) - 2024-04-12

<small>[Compare with 1.2.0](https://github.com/machshev/aramaic-bible-modules/compare/1.2.0...1.2.1)</small>

## [1.2.0](https://github.com/machshev/aramaic-bible-modules/releases/tag/1.2.0) - 2024-04-12

<small>[Compare with first commit](https://github.com/machshev/aramaic-bible-modules/compare/a5f4d34d7f9d50e88fa6188df613db95ea7741ea...1.2.0)</small>

### Build

- significant refactor of the build scripts using copier-pdm template ([78ad8e3](https://github.com/machshev/aramaic-bible-modules/commit/78ad8e388ac84e4bf3f56286ffa09126c0363cf0) by David James McCorrie).
- add auto-changelog ([71d5ecb](https://github.com/machshev/aramaic-bible-modules/commit/71d5ecb894da82b38c0279ad9f37a5e6140c0333) by David James McCorrie).
- update the pdm lock with latest versions ([e578bca](https://github.com/machshev/aramaic-bible-modules/commit/e578bcaa03f9d493cbfca03dfbff2cea34056509) by David James McCorrie).
- update dependancy versions ([25901b6](https://github.com/machshev/aramaic-bible-modules/commit/25901b6a4231172e0fa3c28d71f702bc50de73ea) by David James McCorrie).
- fixed the pyproject.toml dep versions imported from poetry ([6f0a6d2](https://github.com/machshev/aramaic-bible-modules/commit/6f0a6d2cb14eda2f24c36524220d153b4ffe8dba) by David James McCorrie).
- add .pdm-python to .gitignore ([f6e7981](https://github.com/machshev/aramaic-bible-modules/commit/f6e79813f5df38a99cd09260f69c365415c4c1d6) by David James McCorrie).
- migrate from poetry to pdm ([6b1a92d](https://github.com/machshev/aramaic-bible-modules/commit/6b1a92d18fda2a53431a234db7cb10b3ddeb8193) by David James McCorrie).

### Features

- add support for final forms, and improve the hebrew translit mappings ([e4407d6](https://github.com/machshev/aramaic-bible-modules/commit/e4407d6ab88255182028f9156dee9fbf92016a1b) by David James McCorrie).
- add initial support for vpl and osis ([7e901d6](https://github.com/machshev/aramaic-bible-modules/commit/7e901d693f1b70da1f300722c405fbd8146e8f1d) by David James McCorrie).
- proper syriac font in generated HTML ([021e3c3](https://github.com/machshev/aramaic-bible-modules/commit/021e3c34420bb5f466c21298b005bb7dafa4a10f) by David James McCorrie).
- add support for HTML bible module generation as well as Markdown ([c047d89](https://github.com/machshev/aramaic-bible-modules/commit/c047d89cb6c0f9fd9dc7d668feed6c36f5c25fa6) by David James McCorrie).
- generate bible text using either Hebrew/syriac unicode alphabets ([7ca9a3d](https://github.com/machshev/aramaic-bible-modules/commit/7ca9a3d4eb79902c6564960466a7aec8848ca4f0) by David James McCorrie).

### Bug Fixes

- tests ([a769fd1](https://github.com/machshev/aramaic-bible-modules/commit/a769fd15d5dd4d373675e3c6c70986315d5a99ec) by David James McCorrie).
- ci only use 3.12 ([8e16abf](https://github.com/machshev/aramaic-bible-modules/commit/8e16abfb0046a6634e5147423d92cf5f41c7abd9) by David James McCorrie).
- add build all modules back to makefile, docs updated ([a412d8d](https://github.com/machshev/aramaic-bible-modules/commit/a412d8d195cc57be39569d88b628d480473311a8) by David James McCorrie).
- github url ([70c8fc5](https://github.com/machshev/aramaic-bible-modules/commit/70c8fc525f080faa6ef7e01436c155da0b8bbd71) by David James McCorrie).

### Code Refactoring

- start to add some more meaningfull structure ([bb0b0b4](https://github.com/machshev/aramaic-bible-modules/commit/bb0b0b45bb14d4bed041ba3af95c0f1e1a336e2b) by David James McCorrie).

## [0.1.0](https://github.com/machshev/aramaic-bible-modules/releases/tag/0.1.0) - 2024-04-12

<small>[Compare with first commit](https://github.com/machshev/aramaic-bible-modules/compare/a5f4d34d7f9d50e88fa6188df613db95ea7741ea...0.1.0)</small>

### Build

- add auto-changelog ([71d5ecb](https://github.com/machshev/aramaic-bible-modules/commit/71d5ecb894da82b38c0279ad9f37a5e6140c0333) by David James McCorrie).
- update the pdm lock with latest versions ([e578bca](https://github.com/machshev/aramaic-bible-modules/commit/e578bcaa03f9d493cbfca03dfbff2cea34056509) by David James McCorrie).
- update dependancy versions ([25901b6](https://github.com/machshev/aramaic-bible-modules/commit/25901b6a4231172e0fa3c28d71f702bc50de73ea) by David James McCorrie).
- fixed the pyproject.toml dep versions imported from poetry ([6f0a6d2](https://github.com/machshev/aramaic-bible-modules/commit/6f0a6d2cb14eda2f24c36524220d153b4ffe8dba) by David James McCorrie).
- add .pdm-python to .gitignore ([f6e7981](https://github.com/machshev/aramaic-bible-modules/commit/f6e79813f5df38a99cd09260f69c365415c4c1d6) by David James McCorrie).
- migrate from poetry to pdm ([6b1a92d](https://github.com/machshev/aramaic-bible-modules/commit/6b1a92d18fda2a53431a234db7cb10b3ddeb8193) by David James McCorrie).

### Features

- add support for final forms, and improve the hebrew translit mappings ([e4407d6](https://github.com/machshev/aramaic-bible-modules/commit/e4407d6ab88255182028f9156dee9fbf92016a1b) by David James McCorrie).
- add initial support for vpl and osis ([7e901d6](https://github.com/machshev/aramaic-bible-modules/commit/7e901d693f1b70da1f300722c405fbd8146e8f1d) by David James McCorrie).
- proper syriac font in generated HTML ([021e3c3](https://github.com/machshev/aramaic-bible-modules/commit/021e3c34420bb5f466c21298b005bb7dafa4a10f) by David James McCorrie).
- add support for HTML bible module generation as well as Markdown ([c047d89](https://github.com/machshev/aramaic-bible-modules/commit/c047d89cb6c0f9fd9dc7d668feed6c36f5c25fa6) by David James McCorrie).
- generate bible text using either Hebrew/syriac unicode alphabets ([7ca9a3d](https://github.com/machshev/aramaic-bible-modules/commit/7ca9a3d4eb79902c6564960466a7aec8848ca4f0) by David James McCorrie).

### Code Refactoring

- start to add some more meaningfull structure ([bb0b0b4](https://github.com/machshev/aramaic-bible-modules/commit/bb0b0b45bb14d4bed041ba3af95c0f1e1a336e2b) by David James McCorrie).
