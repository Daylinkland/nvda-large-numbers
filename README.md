# Large Number Reader — NVDA add-on

An NVDA add-on that speaks long numbers as words instead of one digit at a time, in English or Spanish.

```
Before:  "one two three five eight nine two"
After:   "one million two hundred thirty five thousand eight hundred ninety two"
Español: "un millón doscientos treinta y cinco mil ochocientos noventa y dos"
```

It works with any synthesizer — Microsoft SAPI, eSpeak, Vocalizer, hardware synths — because it rewrites the text NVDA is about to speak, not the voice. It uses NVDA's official speech filter extension point (`speech.extensions.filter_speechSequence`), so nothing else in NVDA changes.

## Requirements

- NVDA 2025.1 or newer
- Windows

## Download

- Latest release, package attached: https://github.com/Daylinkland/nvda-large-numbers/releases/latest
- Direct file: https://github.com/Daylinkland/nvda-large-numbers/releases/download/v1.2/largeNumberReader-1.2.nvda-addon
- Also in the repository: `largeNumberReader-1.2.nvda-addon` and `Large-Number-Reader-1.2.zip`

## Install

1. Download `largeNumberReader-1.2.nvda-addon` from a link above.
2. Press Enter on the file, or right-click it and choose Install.
3. Answer Yes to the install question, then let NVDA restart.

To confirm it is running: NVDA menu, Tools, Add-on Store, Installed add-ons, look for "Large Number Reader" 1.2.

To remove it: NVDA menu, Tools, Add-on Store, Installed add-ons, select Large Number Reader, Remove.

## Keys

| Key | Action |
| --- | --- |
| NVDA+8 | Turns large number reading on or off. Remembered between sessions. |

Change the key in NVDA menu, Preferences, Input Gestures, Large Number Reader.

## Languages

English and Spanish are built in. By default the number language follows NVDA's own language, so a Spanish NVDA speaks Spanish numbers with nothing to configure.

To force a language: NVDA menu, Preferences, Settings, Large Number Reader, choose the number language. "Automatic" follows NVDA again. The choice is saved.

Spanish is not a word-for-word translation of English:

- it uses the long scale, so *billón* is 10^12 and 10^9 is *mil millones*
- it shortens words before a scale: *un millón*, *veintiún mil*, *treinta y un mil*
- 1000 is *mil*, never *un mil*

Example values:

| Number | English | Spanish |
| --- | --- | --- |
| 1500000 | one million five hundred thousand | un millón quinientos mil |
| 1235892 | one million two hundred thirty five thousand eight hundred ninety two | un millón doscientos treinta y cinco mil ochocientos noventa y dos |
| 1000000000000000 | one quadrillion | mil billones |

## What it leaves alone

Rewriting is deliberately conservative, so unrelated text keeps working:

- numbers shorter than seven digits, so ordinary numbers are read as before
- numbers with a leading zero, such as `01234567` (IDs)
- numbers glued to letters, such as `0x1234567` or `abc123456`
- version and IP style text, such as `2026.2` or `192.168.1.100`
- phone style pairs, such as `555-1234567`
- numbers straight after a currency sign, such as `$1234567`
- anything spoken while spelling or reading character by character

Comma grouped numbers work too: `1,235,892` is read the same as `1235892`.

## Limits

- Up to 36 digits get proper scale names. Longer numbers are still broken into groups of three digits rather than one long digit string, but without scale names.
- Speech only: braille and the text on screen still show the original digits.
- If a voice pronounces a word oddly, edit the words in `addon/globalPlugins/largeNumberReader/data/` (the `number_words` files must keep exactly 1000 lines, line 0 is zero). The add-on falls back to its built-in wording if a file is missing or damaged.

## How it works

The add-on registers one handler with NVDA's speech filter. For each piece of text NVDA is about to speak it finds digit runs that look like quantities, then replaces them with words. Everything else passes through untouched, and any error is logged while the original text is spoken, so speech never breaks.

Number data is small: 1000 words per language for any group of three digits, plus the scale names, reused for every group. A literal "one million to nine hundred ninety nine million" file would be about 20 GB per scale.

## Development

No dependencies beyond Python 3 and NVDA itself.

```
python build_addon.py               # regenerate word files and the .nvda-addon
python tests/test_number_reader.py  # run the test suite
```

The tests load the plugin the way NVDA does — as a package, with the plugin folder absent from `sys.path` — and also exercise the settings panel through stand-ins for NVDA's settings API. That matters: an add-on that passes only when its folder is on `sys.path` will fail to load inside NVDA.

Layout:

```
addon/                          the unpacked add-on
  manifest.ini
  doc/en/readme.html            help shown by NVDA
  globalPlugins/largeNumberReader/
    __init__.py                 plugin: speech filter, toggle, language, settings panel
    languages.py                English and Spanish wording and grammar
    numberwords.py              finds digit runs in speech
    data/                       word tables (English and Spanish)
build_addon.py                  builds the package
tests/test_number_reader.py     automated tests
to-share/README.txt             instructions shipped inside the share zip
```

## Licence

MIT — see `LICENSE`. NVDA add-ons are often published under GPL v2; that is a viable alternative if you prefer it.
