# -*- coding: utf-8 -*-
"""Tests for the Large Number Reader add-on.

The expansion tests run the real logic modules (English and Spanish). The
plugin tests load the real plugin file with small stand-ins for the NVDA
modules it imports, so the speech filter, the NVDA+8 toggle, the language
setting and the settings handling are all exercised without needing NVDA.

Run:  python tests/test_number_reader.py
"""

import importlib.util
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLUGIN_DIR = os.path.join(ROOT, "addon", "globalPlugins", "largeNumberReader")

sys.path.insert(0, PLUGIN_DIR)
import languages  # noqa: E402
import numberwords  # noqa: E402


class NumberWordsTests(unittest.TestCase):
	def check(self, text, expected):
		self.assertEqual(numberwords.expand_text(text), expected)

	def test_millions(self):
		self.check("1500000", "one million five hundred thousand")
		self.check("1000000", "one million")
		self.check("2000000", "two million")

	def test_mixed_number(self):
		self.check(
			"1235892",
			"one million two hundred thirty five thousand eight hundred ninety two",
		)

	def test_billions_and_beyond(self):
		self.check(
			"1234567890",
			"one billion two hundred thirty four million five hundred sixty seven "
			"thousand eight hundred ninety",
		)
		self.check("1000000000000000", "one quadrillion")
		self.check("100000000000000", "one hundred trillion")

	def test_decillion_limit(self):
		digits = "9" * 36
		out = numberwords.expand_text(digits)
		self.assertTrue(out.startswith("nine hundred ninety nine decillion"), out)
		# 37 digits: still chunked, never one long digit string
		out = numberwords.expand_text("9" * 37)
		self.assertIn(",", out)
		self.assertNotIn("0", out)

	def test_grouped_with_commas(self):
		self.check(
			"1,235,892",
			"one million two hundred thirty five thousand eight hundred ninety two",
		)

	def test_embedded_in_sentence(self):
		self.check(
			"cost is 2500000 dollars",
			"cost is two million five hundred thousand dollars",
		)

	def test_small_numbers_untouched(self):
		for text in ("500000", "123456", "0", "42", "2026"):
			self.assertEqual(numberwords.expand_text(text), text)

	def test_things_that_must_not_change(self):
		untouched = [
			"01234567",              # identifier with a leading zero
			"0x1234567",             # glued to letters
			"abc1234567",            # glued to letters
			"2026.2",                # version
			"192.168.1.100",         # IP address
			"555-1234567",           # phone style pair
			"$1234567",              # currency
			"1234567.89",            # decimal
			"file 1234567.txt",      # filename (dot after the digits)
			"12:3456789",            # time-like
			"version 1234567",       # plain run should still expand, see below
		]
		for text in untouched[:-1]:
			self.assertEqual(numberwords.expand_text(text), text, text)
		self.assertEqual(
			numberwords.expand_text(untouched[-1]),
			"version one million two hundred thirty four thousand five hundred sixty seven",
		)

	def test_sentence_punctuation_after_number(self):
		self.check(
			"The total is 1500000.",
			"The total is one million five hundred thousand.",
		)
		self.check(
			"It was 1500000, then 2500000.",
			"It was one million five hundred thousand, then two million five hundred thousand.",
		)

	def test_multiple_numbers_in_one_message(self):
		out = numberwords.expand_text("1234567 and 7654321")
		self.assertEqual(
			out,
			"one million two hundred thirty four thousand five hundred sixty seven "
			"and seven million six hundred fifty four thousand three hundred twenty one",
		)

	def test_empty_and_no_digits(self):
		self.assertEqual(numberwords.expand_text(""), "")
		self.assertEqual(numberwords.expand_text("hello there"), "hello there")

	def test_english_data_files_are_used(self):
		# The built data file lists every group 0..999.
		self.assertEqual(len(languages.EN_GROUP_WORDS), 1000)
		self.assertEqual(languages.EN_GROUP_WORDS[0], "zero")
		self.assertEqual(languages.EN_GROUP_WORDS[999], "nine hundred ninety nine")
		self.assertEqual(languages.EN_GROUP_WORDS[842], "eight hundred forty two")
		self.assertEqual(languages.EN_SCALE_WORDS[0], "thousand")
		self.assertEqual(languages.EN_SCALE_WORDS[-1], "decillion")


class SpanishTests(unittest.TestCase):
	def words(self, digits):
		return languages.number_to_words(digits, "es")

	def test_group_words(self):
		cases = {
			0: "cero",
			1: "uno",
			15: "quince",
			16: "dieciséis",
			20: "veinte",
			21: "veintiuno",
			22: "veintidós",
			30: "treinta",
			31: "treinta y uno",
			100: "cien",
			101: "ciento uno",
			110: "ciento diez",
			200: "doscientos",
			500: "quinientos",
			700: "setecientos",
			900: "novecientos",
			999: "novecientos noventa y nueve",
		}
		for number, expected in cases.items():
			self.assertEqual(languages.spanish_group_word(number), expected, number)

	def test_millions(self):
		self.assertEqual(self.words("1000000"), "un millón")
		self.assertEqual(self.words("2000000"), "dos millones")
		self.assertEqual(self.words("1500000"), "un millón quinientos mil")

	def test_mixed_number(self):
		self.assertEqual(
			self.words("1235892"),
			"un millón doscientos treinta y cinco mil ochocientos noventa y dos",
		)

	def test_thousands(self):
		self.assertEqual(self.words("1000"), "mil")
		self.assertEqual(self.words("31000"), "treinta y un mil")
		self.assertEqual(self.words("100000"), "cien mil")
		self.assertEqual(self.words("21000"), "veintiún mil")

	def test_short_form_before_scale(self):
		self.assertEqual(self.words("21000000"), "veintiún millones")
		self.assertEqual(self.words("31000000"), "treinta y un millones")
		self.assertEqual(self.words("1000000000000"), "un billón")

	def test_long_scale(self):
		# Spanish billón is 10^12, and 10^9 has no single word.
		self.assertEqual(self.words("1000000000"), "mil millones")
		self.assertEqual(self.words("2000000000"), "dos mil millones")
		self.assertEqual(self.words("100000000000000"), "cien billones")
		self.assertEqual(self.words("1000000000000000"), "mil billones")
		self.assertEqual(self.words("2000000000000000"), "dos mil billones")

	def test_spanish_text_expansion(self):
		self.assertEqual(
			numberwords.expand_text("cuesta 2500000 dólares", "es"),
			"cuesta dos millones quinientos mil dólares",
		)
		self.assertEqual(
			numberwords.expand_text("1,235,892", "es"),
			"un millón doscientos treinta y cinco mil ochocientos noventa y dos",
		)

	def test_spanish_leaves_same_things_alone(self):
		for text in (
			"500000",
			"01234567",
			"0x1234567",
			"2026.2",
			"192.168.1.100",
			"555-1234567",
			"$1234567",
			"1234567.89",
		):
			self.assertEqual(numberwords.expand_text(text, "es"), text, text)

	def test_spanish_data_files_are_used(self):
		self.assertEqual(len(languages.ES_GROUP_WORDS), 1000)
		self.assertEqual(languages.ES_GROUP_WORDS[0], "cero")
		self.assertEqual(languages.ES_GROUP_WORDS[999], "novecientos noventa y nueve")
		self.assertEqual(languages.ES_SCALE_WORDS[0], "mil")
		self.assertEqual(languages.ES_SCALE_WORDS[1], "millón")
		self.assertEqual(languages.ES_SCALE_WORDS[2], "mil millones")
		self.assertEqual(languages.ES_SCALE_WORDS[3], "billón")

	def test_language_normalization(self):
		self.assertEqual(languages.normalize("es_ES"), "es")
		self.assertEqual(languages.normalize("ES-es"), "es")
		self.assertEqual(languages.normalize("es"), "es")
		self.assertEqual(languages.normalize("fr"), "en")
		self.assertEqual(languages.normalize(None), "en")
		self.assertEqual(languages.name("es"), "Spanish")
		self.assertIn("es", languages.available())


def install_fake_nvda():
	"""Put minimal stand-ins for NVDA modules into sys.modules."""
	for name in list(sys.modules):
		if name == "largeNumberReader" or name.startswith("largeNumberReader."):
			del sys.modules[name]
	for name in ("gui", "gui.guiHelper", "gui.settingsDialogs", "wx"):
		sys.modules.pop(name, None)

	gp_module = types.ModuleType("globalPluginHandler")

	class GlobalPlugin:
		scriptCategory = ""

		def __init__(self):
			pass

		def terminate(self):
			pass

	gp_module.GlobalPlugin = GlobalPlugin
	sys.modules["globalPluginHandler"] = gp_module

	commands = types.ModuleType("speech.commands")

	class CharacterModeCommand:
		def __init__(self, state=True):
			self.state = state

	commands.CharacterModeCommand = CharacterModeCommand

	extensions = types.ModuleType("speech.extensions")

	class FakeFilter:
		def __init__(self):
			self.handlers = []

		def register(self, handler):
			self.handlers.append(handler)

		def unregister(self, handler):
			if handler in self.handlers:
				self.handlers.remove(handler)

		def apply(self, value):
			for handler in self.handlers:
				value = handler(value)
			return value

	extensions.filter_speechSequence = FakeFilter()

	speech_module = types.ModuleType("speech")
	speech_module.extensions = extensions
	speech_module.commands = commands
	sys.modules["speech"] = speech_module
	sys.modules["speech.extensions"] = extensions
	sys.modules["speech.commands"] = commands

	class Section(dict):
		pass

	class Conf:
		def __init__(self):
			self.spec = {}
			self.sections = {}

		def __getitem__(self, key):
			return self.sections.setdefault(key, Section())

	config_module = types.ModuleType("config")
	config_module.conf = Conf()
	sys.modules["config"] = config_module

	ui_module = types.ModuleType("ui")
	ui_module.messages = []
	ui_module.message = ui_module.messages.append
	sys.modules["ui"] = ui_module

	script_module = types.ModuleType("scriptHandler")

	def script(**kwargs):
		def decorate(function):
			function.scriptInfo = kwargs
			return function

		return decorate

	script_module.script = script
	sys.modules["scriptHandler"] = script_module

	log_module = types.ModuleType("logHandler")

	class Log:
		def __init__(self):
			self.errors = []

		def exception(self, message, *args, **kwargs):
			self.errors.append(message)

		def info(self, message, *args, **kwargs):
			pass

	log_module.log = Log()
	sys.modules["logHandler"] = log_module

	return speech_module, config_module, ui_module, log_module


def install_fake_gui():
	"""Stand-ins for NVDA's settings dialog, so the panel can be tested."""
	wx = types.ModuleType("wx")

	class Choice:
		def __init__(self, parent=None, choices=None):
			self.choices = list(choices or [])
			self.selection = 0

		def SetSelection(self, index):
			self.selection = index

		def GetSelection(self):
			return self.selection

	wx.Choice = Choice
	sys.modules["wx"] = wx

	guiHelper = types.ModuleType("gui.guiHelper")

	class BoxSizerHelper:
		def __init__(self, *args, **kwargs):
			pass

		def addLabeledControl(self, label, controlClass, **kwargs):
			control = controlClass(choices=kwargs.get("choices"))
			self.control = control
			return control

	guiHelper.BoxSizerHelper = BoxSizerHelper

	gui = types.ModuleType("gui")
	gui.__path__ = []
	gui.guiHelper = guiHelper

	settingsDialogs = types.ModuleType("gui.settingsDialogs")

	class SettingsPanel:
		title = ""

		def __init__(self, parent=None):
			self.parent = parent

	class NVDASettingsDialog:
		categoryClasses = []

	settingsDialogs.SettingsPanel = SettingsPanel
	settingsDialogs.NVDASettingsDialog = NVDASettingsDialog

	sys.modules["gui"] = gui
	sys.modules["gui.guiHelper"] = guiHelper
	sys.modules["gui.settingsDialogs"] = settingsDialogs
	return settingsDialogs


def load_plugin():
	spec = importlib.util.spec_from_file_location(
		"largeNumberReader",
		os.path.join(PLUGIN_DIR, "__init__.py"),
		submodule_search_locations=[PLUGIN_DIR],
	)
	module = importlib.util.module_from_spec(spec)
	sys.modules["largeNumberReader"] = module
	# NVDA loads the plugin as a package and does not put the plugin folder on
	# sys.path, so mirror that here: any sibling import must work relatively.
	savedPath = list(sys.path)
	sys.path[:] = [p for p in sys.path if os.path.normcase(p) != os.path.normcase(PLUGIN_DIR)]
	try:
		spec.loader.exec_module(module)
	finally:
		sys.path[:] = savedPath
	return module


class PluginTests(unittest.TestCase):
	def setUp(self):
		self.speech, self.config, self.ui, self.log = install_fake_nvda()
		self.plugin_module = load_plugin()
		self.plugin = self.plugin_module.GlobalPlugin()
		self.filter = self.speech.extensions.filter_speechSequence

	def test_filter_is_registered_once(self):
		self.assertEqual(len(self.filter.handlers), 1)

	def test_sequence_gets_expanded(self):
		sequence = ["total 1235892 items"]
		result = self.filter.apply(sequence)
		self.assertEqual(
			result,
			["total one million two hundred thirty five thousand eight hundred ninety two items"],
		)

	def test_commands_pass_through(self):
		pitch = object()
		result = self.filter.apply([pitch, "1500000"])
		self.assertIs(result[0], pitch)
		self.assertEqual(result[1], "one million five hundred thousand")

	def test_unchanged_sequence_is_returned_as_is(self):
		sequence = ["nothing to do here"]
		self.assertIs(self.filter.apply(sequence), sequence)

	def test_nvda_plus_8_toggles(self):
		gestures = self.plugin._GlobalPlugin__gestures
		self.assertIn("kb:NVDA+8", gestures)
		self.assertEqual(gestures["kb:NVDA+8"], "toggleNumberReading")
		self.assertTrue(hasattr(self.plugin, "script_toggleNumberReading"))

		self.plugin.script_toggleNumberReading(None)
		self.assertFalse(self.plugin._enabled)
		self.assertEqual(self.filter.apply(["1500000"]), ["1500000"])
		self.assertEqual(self.ui.messages[-1], "Large number reading off")

		self.plugin.script_toggleNumberReading(None)
		self.assertTrue(self.plugin._enabled)
		self.assertEqual(self.filter.apply(["1500000"]), ["one million five hundred thousand"])
		self.assertEqual(self.ui.messages[-1], "Large number reading on")

	def test_toggle_is_saved_to_config(self):
		self.plugin.script_toggleNumberReading(None)
		self.assertFalse(self.config.conf["largeNumberReader"]["enabled"])

	def test_saved_off_setting_is_respected_on_load(self):
		# Simulate a fresh NVDA start: no plugin yet, and the saved value is off.
		self.filter.handlers.clear()
		self.config.conf["largeNumberReader"]["enabled"] = False
		plugin = self.plugin_module.GlobalPlugin()
		self.assertFalse(plugin._enabled)
		self.assertEqual(self.filter.apply(["1500000"]), ["1500000"])

	def test_character_mode_is_left_alone(self):
		command = self.speech.commands.CharacterModeCommand(True)
		self.assertEqual(self.filter.apply([command, "1500000"]), [command, "1500000"])

	def test_character_mode_off_does_not_block(self):
		command = self.speech.commands.CharacterModeCommand(False)
		result = self.filter.apply([command, "1500000"])
		self.assertEqual(result[1], "one million five hundred thousand")

	def test_no_logged_errors(self):
		self.filter.apply(["1235892", "plain"])
		self.assertEqual(self.log.log.errors, [])

	def test_terminate_unregisters(self):
		self.plugin.terminate()
		self.assertEqual(self.filter.handlers, [])

	def test_language_defaults_to_automatic(self):
		self.assertEqual(self.plugin._languageSetting, "auto")
		# No NVDA language available in the harness, so English is used.
		self.assertEqual(self.plugin._numberLanguage(), "en")

	def test_setting_spanish_changes_speech(self):
		self.plugin.setLanguageSetting("es")
		self.assertEqual(self.filter.apply(["1500000"]), ["un millón quinientos mil"])
		self.assertEqual(self.config.conf["largeNumberReader"]["language"], "es")
		self.assertEqual(self.plugin._numberLanguage(), "es")

	def test_unknown_saved_language_falls_back_to_english(self):
		self.plugin.setLanguageSetting("klingon")
		self.assertEqual(self.filter.apply(["1500000"]), ["one million five hundred thousand"])

	def test_saved_language_is_used_on_load(self):
		self.filter.handlers.clear()
		self.config.conf["largeNumberReader"]["language"] = "es"
		self.plugin_module.GlobalPlugin()
		self.assertEqual(self.filter.apply(["1500000"]), ["un millón quinientos mil"])

	def test_settings_panel_is_optional(self):
		# There is no GUI in the test harness; the plugin must work regardless.
		self.assertIsNone(self.plugin_module.GlobalPlugin._settingsPanelClass)


class SettingsPanelTests(unittest.TestCase):
	"""The panel NVDA's Settings dialog lists, exercised through stand-ins."""

	def setUp(self):
		self.speech, self.config, self.ui, self.log = install_fake_nvda()
		self.settingsDialogs = install_fake_gui()
		self.plugin_module = load_plugin()
		self.plugin = self.plugin_module.GlobalPlugin()

	def speechOutput(self, text="1500000"):
		return self.speech.extensions.filter_speechSequence.apply([text])[0]

	def test_panel_is_registered(self):
		self.assertIsNotNone(self.plugin._settingsPanelClass)
		self.assertIn(
			self.plugin._settingsPanelClass,
			self.settingsDialogs.NVDASettingsDialog.categoryClasses,
		)

	def test_panel_has_the_add_on_title(self):
		self.assertEqual(self.plugin._settingsPanelClass.title, "Large Number Reader")

	def test_panel_offers_automatic_first_then_languages(self):
		panel = self.plugin._settingsPanelClass(None)
		panel.makeSettings(object())
		self.assertEqual(panel._codes, ["auto", "en", "es"])
		self.assertEqual(panel.languageChoice.GetSelection(), 0)

	def test_panel_saves_the_chosen_language(self):
		panel = self.plugin._settingsPanelClass(None)
		panel.makeSettings(object())
		panel.languageChoice.SetSelection(panel._codes.index("es"))
		panel.onSave()
		self.assertEqual(self.config.conf["largeNumberReader"]["language"], "es")
		self.assertEqual(self.speechOutput(), "un millón quinientos mil")

	def test_panel_shows_the_saved_language(self):
		self.config.conf["largeNumberReader"]["language"] = "es"
		plugin = self.plugin_module.GlobalPlugin()
		panel = plugin._settingsPanelClass(None)
		panel.makeSettings(object())
		self.assertEqual(panel.languageChoice.GetSelection(), panel._codes.index("es"))

	def test_panel_is_removed_on_terminate(self):
		panel = self.plugin._settingsPanelClass
		self.plugin.terminate()
		self.assertNotIn(panel, self.settingsDialogs.NVDASettingsDialog.categoryClasses)


if __name__ == "__main__":
	unittest.main(verbosity=2)
