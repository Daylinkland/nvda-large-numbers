# -*- coding: utf-8 -*-
"""Find long digit runs in text and replace them with spoken words.

This module is only the scanner: it decides which digit runs are real
quantities worth spelling out (and which are IDs, versions, phone numbers and
so on). The words themselves come from languages.py, so adding a language
never means touching this file.

This module deliberately has NO NVDA imports, so it can be tested (and
reasoned about) on its own. The NVDA plugin in __init__.py is a thin shell
around expand_text().
"""

import re

try:
	# Normal case: NVDA loads this file as part of the add-on package, where a
	# sibling module must be imported relatively.
	from . import languages
except ImportError:
	# Standalone use (running the tests or the build script directly).
	import languages

MAX_GROUPS = languages.MAX_GROUPS
MAX_DIGITS = languages.MAX_DIGITS

# A number starting at a word/path boundary. Grouped numbers (1,235,892) and
# plain runs of 7+ digits are both matched; things glued to letters, slashes,
# colons, handles or currency signs are left alone. A comma or full stop after
# the digits is checked separately, because "total 1500000." should still be
# expanded while "1234567.89" and "1234567.txt" must not be.
_PATTERN = re.compile(
	r"(?<![0-9A-Za-z._:/\\#$€£¥%])"
	r"(?:\d{1,3}(?:,\d{3}){2,}|\d{7,})"
	r"(?![0-9A-Za-z_:\\/$€£¥%-])"
)

_DIGIT = re.compile(r"\d")

# A current/max pair, such as a game's health bar (3486099252615/4470515485023)
# or "damage/needed". A slash normally means "this is not a quantity", which
# left both numbers being read out one digit at a time, but both halves really
# are quantities, so both are spelled out and the slash is kept between them.
_PAIR = re.compile(
	r"(?<![0-9A-Za-z._:/\\#$€£¥%])"
	r"(\d{1,3}(?:,\d{3}){2,}|\d{7,})"
	r"(\s*/\s*)"
	r"(\d{1,3}(?:,\d{3}){2,}|\d{7,})"
	r"(?![0-9A-Za-z_:\\/$€£¥%-])"
)


def group_word(number, language=None):
	"""Words for 0 to 999 in the chosen language."""
	code = languages.normalize(language)
	if code == "es":
		return languages.spanish_group_word(number)
	return languages.english_group_word(number)


def split_groups(digits):
	return languages.split_groups(digits)


def number_to_words(digits, language=None):
	"""Turn a pure digit string into words in the chosen language."""
	return languages.number_to_words(digits, language)


def _is_blocked_by_dot_or_comma(text, end):
	"""True for 1234567.89 and 1234567.txt, but not for a full stop after the digits."""
	if end >= len(text) or text[end] not in ".,":
		return False
	if end + 1 >= len(text):
		return False
	following = text[end + 1]
	return following.isalnum()


def _is_blocked_by_hyphen(text, start):
	"""True for things like 555-1234567, where '-' joins two numbers."""
	if start == 0 or text[start - 1] != "-":
		return False
	if start >= 2 and (text[start - 2].isalnum() or text[start - 2] == "_"):
		return True
	return False


def expand_match(text, match, language=None):
	digits = match.group().replace(",", "")
	if len(digits) < 7:
		return match.group()
	if digits[0] == "0":
		# Leading zeros mean an identifier, not a quantity.
		return match.group()
	if _is_blocked_by_hyphen(text, match.start()):
		return match.group()
	if _is_blocked_by_dot_or_comma(text, match.end()):
		return match.group()
	return number_to_words(digits, language)


def _side_words(digits, language=None):
	"""Words for one half of a pair, or None when it is not a quantity."""
	plain = digits.replace(",", "")
	if len(plain) < 7 or plain[0] == "0":
		return None
	return number_to_words(plain, language)


def expand_pairs(text, language=None):
	"""Spell out both halves of current/max pairs such as 1500000/2000000."""

	def replace(match):
		if _is_blocked_by_dot_or_comma(text, match.end()):
			return match.group()
		first, separator, second = match.group(1), match.group(2), match.group(3)
		left = _side_words(first, language)
		right = _side_words(second, language)
		if left is None and right is None:
			return match.group()
		return (left or first) + separator + (right or second)

	return _PAIR.sub(replace, text)


def expand_text(text, language=None):
	"""Return text with every large number written out in the chosen language."""
	if not text or len(text) < 7 or _DIGIT.search(text) is None:
		return text

	if _PAIR.search(text):
		text = expand_pairs(text, language)

	def replace(match):
		return expand_match(text, match, language)

	return _PATTERN.sub(replace, text)
