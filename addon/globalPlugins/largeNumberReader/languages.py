# -*- coding: utf-8 -*-
"""Turn digit strings into words, in more than one language.

numberwords.py finds the digit runs in a piece of text; this module turns a
digit string into spoken words. Each language brings its own word tables and
its own rules, because the rules really do differ:

  English: 1235892 -> "one million two hundred thirty five thousand ..."
  Spanish: 1235892 -> "un millón doscientos treinta y cinco mil ..."

Spanish is not a word-for-word swap of English. It uses the long scale, so
"billón" is a million millions (10^12) and there is no word for 10^9 other
than "mil millones". It also shortens "uno" to "un" and "veintiuno" to
"veintiún" in front of a scale ("un millón", "veintiún mil"), and 1000 is
"mil", never "un mil".

No NVDA imports here on purpose, so everything can be tested on its own.
"""

import os

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

DEFAULT_LANGUAGE = "en"
AUTOMATIC = "auto"


def split_groups(digits):
	"""Split a digit string into 3 digit groups, most significant first."""
	groups = []
	end = len(digits)
	while end > 0:
		start = max(0, end - 3)
		groups.insert(0, int(digits[start:end]))
		end = start
	return groups


def _load_lines(path, expected_count):
	"""Read a word list, ignoring blank lines and # comments.

	Returns None when the file is missing or the wrong shape, so the built in
	words are used instead. A broken data file must never stop NVDA speaking.
	"""
	try:
		with open(path, "r", encoding="utf-8-sig") as handle:
			lines = [line.strip() for line in handle]
	except Exception:
		return None
	lines = [line for line in lines if line and not line.startswith("#")]
	if len(lines) != expected_count:
		return None
	return tuple(lines)


# ------------------------------------------------------------------ English

EN_ONES = (
	"zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
	"nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
	"sixteen", "seventeen", "eighteen", "nineteen",
)
EN_TENS = (
	"", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
	"eighty", "ninety",
)

EN_SCALES = (
	"thousand",
	"million",
	"billion",
	"trillion",
	"quadrillion",
	"quintillion",
	"sextillion",
	"septillion",
	"octillion",
	"nonillion",
	"decillion",
)


def english_generated_group_word(number):
	"""English words for 0 to 999, built in code (the fallback table)."""
	if number < 0 or number > 999:
		raise ValueError("group must be 0 to 999")
	if number == 0:
		return EN_ONES[0]
	parts = []
	remainder = number
	if remainder >= 100:
		parts.append(EN_ONES[remainder // 100] + " hundred")
		remainder = remainder % 100
	if remainder >= 20:
		parts.append(EN_TENS[remainder // 10])
		if remainder % 10:
			parts.append(EN_ONES[remainder % 10])
	elif remainder > 0:
		parts.append(EN_ONES[remainder])
	return " ".join(parts)


EN_GROUP_WORDS = _load_lines(os.path.join(_DATA_DIR, "number_words.txt"), 1000)
if EN_GROUP_WORDS is None:
	EN_GROUP_WORDS = tuple(english_generated_group_word(n) for n in range(1000))

EN_SCALE_WORDS = _load_lines(os.path.join(_DATA_DIR, "scale_words.txt"), len(EN_SCALES))
if EN_SCALE_WORDS is None:
	EN_SCALE_WORDS = EN_SCALES

EN_MAX_GROUPS = len(EN_SCALE_WORDS) + 1


def english_group_word(number):
	if 0 <= number < len(EN_GROUP_WORDS):
		return EN_GROUP_WORDS[number]
	return english_generated_group_word(number)


def english_number_to_words(digits):
	"""Turn a pure digit string into English words."""
	groups = split_groups(digits)
	if len(groups) > EN_MAX_GROUPS:
		# Beyond decillions: read it as 3 digit chunks so it still cannot come
		# out as one long string of digits.
		return ", ".join(str(group) for group in groups)
	count = len(groups)
	parts = []
	for position, group in enumerate(groups):
		if group == 0:
			continue
		scaleIndex = count - 1 - position
		words = english_group_word(group)
		if scaleIndex > 0:
			words += " " + EN_SCALE_WORDS[scaleIndex - 1]
		parts.append(words)
	return " ".join(parts)


# ------------------------------------------------------------------ Spanish

ES_UNITS = (
	"cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
	"nueve", "diez", "once", "doce", "trece", "catorce", "quince",
)
ES_TEENS = ("dieciséis", "diecisiete", "dieciocho", "diecinueve")
ES_TWENTIES = (
	"veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro",
	"veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve",
)
ES_TENS = (
	"", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta",
	"ochenta", "noventa",
)
ES_HUNDREDS = (
	"", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
	"seiscientos", "setecientos", "ochocientos", "novecientos",
)

# Long scale, as used in Spain and most of Latin America: billón is 10^12.
ES_SCALES = (
	"mil",                # 10^3
	"millón",             # 10^6
	"mil millones",       # 10^9
	"billón",             # 10^12
	"mil billones",       # 10^15
	"trillón",            # 10^18
	"mil trillones",      # 10^21
	"cuatrillón",         # 10^24
	"mil cuatrillones",   # 10^27
	"quintillón",         # 10^30
	"mil quintillones",   # 10^33
)


def spanish_generated_group_word(number):
	"""Spanish words for 0 to 999, in their full (not shortened) form."""
	if number < 0 or number > 999:
		raise ValueError("group must be 0 to 999")
	if number < 16:
		return ES_UNITS[number]
	if number < 20:
		return ES_TEENS[number - 16]
	if number < 30:
		return ES_TWENTIES[number - 20]
	if number < 100:
		tens, unit = divmod(number, 10)
		word = ES_TENS[tens]
		if unit:
			word += " y " + ES_UNITS[unit]
		return word
	hundreds, rest = divmod(number, 100)
	if hundreds == 1 and rest == 0:
		return "cien"
	word = ES_HUNDREDS[hundreds]
	if rest:
		word += " " + spanish_generated_group_word(rest)
	return word


ES_GROUP_WORDS = _load_lines(os.path.join(_DATA_DIR, "number_words_es.txt"), 1000)
if ES_GROUP_WORDS is None:
	ES_GROUP_WORDS = tuple(spanish_generated_group_word(n) for n in range(1000))

ES_SCALE_WORDS = _load_lines(os.path.join(_DATA_DIR, "scale_words_es.txt"), len(ES_SCALES))
if ES_SCALE_WORDS is None:
	ES_SCALE_WORDS = ES_SCALES

ES_MAX_GROUPS = len(ES_SCALE_WORDS) + 1


def spanish_group_word(number):
	if 0 <= number < len(ES_GROUP_WORDS):
		return ES_GROUP_WORDS[number]
	return spanish_generated_group_word(number)


def spanish_apocopate(word):
	"""The short form used in front of a scale word.

	uno -> un, veintiuno -> veintiún, "treinta y uno" -> "treinta y un".
	"""
	if word == "uno":
		return "un"
	if word == "veintiuno":
		return "veintiún"
	suffix = " y uno"
	if word.endswith(suffix):
		return word[: -len(suffix)] + " y un"
	return word


def spanish_scale_word(scale_index, plural):
	"""Scale name for a group, pluralised when the group is not one."""
	word = ES_SCALE_WORDS[scale_index - 1]
	if plural and word.endswith("ón"):
		# millón -> millones, billón -> billones, trillón -> trillones ...
		return word[:-2] + "ones"
	return word


def spanish_number_to_words(digits):
	"""Turn a pure digit string into Spanish words."""
	groups = split_groups(digits)
	if len(groups) > ES_MAX_GROUPS:
		return ", ".join(str(group) for group in groups)
	count = len(groups)
	parts = []
	for position, group in enumerate(groups):
		if group == 0:
			continue
		scaleIndex = count - 1 - position
		if scaleIndex == 0:
			parts.append(spanish_group_word(group))
			continue
		if group == 1 and scaleIndex % 2 == 1:
			# "mil", "mil millones", "mil billones": never "un mil".
			parts.append(spanish_scale_word(scaleIndex, False))
			continue
		words = spanish_apocopate(spanish_group_word(group))
		parts.append(words + " " + spanish_scale_word(scaleIndex, group != 1))
	return " ".join(parts) if parts else ES_UNITS[0]


# ----------------------------------------------------------------- registry

EN_STRINGS = {
	"readingOn": "Large number reading on",
	"readingOff": "Large number reading off",
	"languageLabel": "Number &language:",
	"automatic": "Automatic (the same as NVDA)",
}

ES_STRINGS = {
	"readingOn": "Lectura de números grandes activada",
	"readingOff": "Lectura de números grandes desactivada",
	"languageLabel": "&Idioma de los números:",
	"automatic": "Automático (el mismo que NVDA)",
}


class Language(object):
	def __init__(self, code, name, nativeName, numberToWords, maxGroups, strings):
		self.code = code
		self.name = name
		self.nativeName = nativeName
		self.numberToWords = numberToWords
		self.maxGroups = maxGroups
		self.strings = strings


LANGUAGES = {
	"en": Language(
		"en", "English", "English", english_number_to_words, EN_MAX_GROUPS, EN_STRINGS
	),
	"es": Language(
		"es", "Spanish", "Español", spanish_number_to_words, ES_MAX_GROUPS, ES_STRINGS
	),
}

MAX_GROUPS = max(language.maxGroups for language in LANGUAGES.values())
MAX_DIGITS = MAX_GROUPS * 3


def normalize(code):
	"""Map "es_ES", "es-ES" or "ES" to "es"; anything unsupported to English."""
	if not code:
		return DEFAULT_LANGUAGE
	base = str(code).replace("-", "_").split("_")[0].strip().lower()
	if base in LANGUAGES:
		return base
	return DEFAULT_LANGUAGE


def available():
	"""Language codes, in a stable order (English first, then alphabetical)."""
	codes = sorted(LANGUAGES)
	return codes


def name(code):
	return LANGUAGES[normalize(code)].name


def native_name(code):
	return LANGUAGES[normalize(code)].nativeName


def number_to_words(digits, language=None):
	code = normalize(language or DEFAULT_LANGUAGE)
	return LANGUAGES[code].numberToWords(digits)


def strings(language=None):
	code = normalize(language or DEFAULT_LANGUAGE)
	return LANGUAGES[code].strings
