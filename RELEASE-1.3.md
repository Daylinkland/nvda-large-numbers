# Large Number Reader 1.3

An NVDA add-on that speaks long numbers as words instead of one digit at a time, in English and Spanish.

```
Before:  one two three five eight nine two
After:   one million two hundred thirty five thousand eight hundred ninety two
Español: un millón doscientos treinta y cinco mil ochocientos noventa y dos
```

## Install

1. Download `largeNumberReader-1.3.nvda-addon` below.
2. Press Enter on it, or right-click and choose Install.
3. Answer Yes, then let NVDA restart.

Requires NVDA 2025.1 or newer. Free, MIT licence, share it with anyone.

If you already have an older version installed, NVDA asks whether to update it: say Yes.

## What changed in 1.3

Symbols next to a number, or between two numbers, no longer break the reading.

A long number sitting against a symbol such as `/` used to be treated as an
identifier and skipped, so it was read out one digit at a time. Both values are
now spoken as words and the symbol is kept where it was:

```
Before:  one five zero zero zero zero zero slash two zero zero zero zero zero zero
Now:     one million five hundred thousand slash two million
```

Everything 1.2 did is unchanged: numbers under seven digits, IDs with leading
zeros, version numbers, IP addresses, decimals, hyphenated phone pairs and
currency amounts are still left exactly as they are.

## Full details

Read the repository for the language rules, the exact cases it skips, and how to build it:

https://github.com/Daylinkland/nvda-large-numbers
