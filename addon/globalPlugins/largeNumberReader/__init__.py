# -*- coding: utf-8 -*-
"""Large Number Reader - an NVDA global plugin.

Rewrites long numbers in outgoing speech so they are spoken as words instead
of being read out digit by digit:

	1235892 -> "one million two hundred thirty five thousand eight hundred ninety two"
	       -> "un millón doscientos treinta y cinco mil ochocientos noventa y dos"

English and Spanish are built in. The number language follows NVDA's own
language automatically, and can be set by hand in NVDA menu, Preferences,
Settings, Large Number Reader.

Toggle with NVDA+8. The setting is remembered between NVDA sessions.

Everything is plain Python on purpose: no new dependencies, no monkey
patching of NVDA internals, no files written outside the add-on. The speech
hook used here (speech.extensions.filter_speechSequence) is the official
extension point NVDA provides for changing text before it reaches the
synthesizer, so other add-ons and NVDA itself keep working.
"""

import globalPluginHandler
import config
import speech
import speech.commands  # noqa: F401 - used for CharacterModeCommand
import speech.extensions  # noqa: F401 - the official speech filter hook
import ui
import scriptHandler
from logHandler import log

try:
	from . import languages
	from . import numberwords
except Exception:  # pragma: no cover - only if the add-on is broken
	languages = None
	numberwords = None
	log.exception("Large Number Reader: number helper failed to load")

CONFIG_SECTION = "largeNumberReader"
SCRIPT_CATEGORY = "Large Number Reader"
PANEL_TITLE = "Large Number Reader"
AUTOMATIC = "auto"
DEFAULT_SETTING = AUTOMATIC


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = SCRIPT_CATEGORY
	_settingsPanelClass = None

	def __init__(self):
		super().__init__()
		self._enabled = True
		self._languageSetting = DEFAULT_SETTING
		try:
			config.conf.spec[CONFIG_SECTION] = {
				"enabled": "boolean(default=True)",
				"language": "string(default='auto')",
			}
			section = config.conf[CONFIG_SECTION]
			self._enabled = bool(section.get("enabled", True))
			self._languageSetting = str(section.get("language", DEFAULT_SETTING) or DEFAULT_SETTING)
		except Exception:
			log.exception("Large Number Reader: could not read saved settings")
		try:
			speech.extensions.filter_speechSequence.register(self.filterSpeechSequence)
		except Exception:
			log.exception("Large Number Reader: could not register the speech filter")
		self._registerSettingsPanel()

	def terminate(self):
		try:
			speech.extensions.filter_speechSequence.unregister(self.filterSpeechSequence)
		except Exception:
			log.exception("Large Number Reader: could not unregister the speech filter")
		self._unregisterSettingsPanel()
		try:
			config.conf.spec.pop(CONFIG_SECTION, None)
		except Exception:
			pass
		super().terminate()

	# ------------------------------------------------------------ languages

	@staticmethod
	def _nvdaLanguageCode():
		"""NVDA's current language, or None when NVDA is not available."""
		try:
			import languageHandler

			return languageHandler.getLanguage()
		except Exception:
			return None

	def _numberLanguage(self):
		"""Code of the language the numbers should be spoken in."""
		if languages is None:
			return None
		if self._languageSetting and self._languageSetting != AUTOMATIC:
			return languages.normalize(self._languageSetting)
		return languages.normalize(self._nvdaLanguageCode())

	def _strings(self):
		"""UI wording in NVDA's own language, falling back to English."""
		if languages is None:
			return {}
		return languages.strings(self._nvdaLanguageCode())

	def setLanguageSetting(self, code):
		"""Called by the settings panel."""
		self._languageSetting = code or DEFAULT_SETTING
		try:
			config.conf[CONFIG_SECTION]["language"] = self._languageSetting
		except Exception:
			log.exception("Large Number Reader: could not save the language setting")

	def _registerSettingsPanel(self):
		if languages is None:
			return
		try:
			import wx
			from gui import guiHelper
			from gui.settingsDialogs import NVDASettingsDialog
			try:
				# Current NVDA names the base class SettingsPanel.
				from gui.settingsDialogs import SettingsPanel as panelBase
			except ImportError:
				# Older NVDA used a different name for the same thing.
				from gui.settingsDialogs import AutoSettingsPanel as panelBase
		except ImportError:
			# No graphical settings dialog here (for example during tests).
			log.info("Large Number Reader: settings panel unavailable")
			return
		except Exception:
			log.exception("Large Number Reader: could not import the settings dialog")
			return

		plugin = self

		class LanguagePanel(panelBase):
			title = PANEL_TITLE

			def makeSettings(self, settingsSizer):
				strings = plugin._strings()
				helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
				codes = [AUTOMATIC] + languages.available()
				choices = [strings.get("automatic", "Automatic (the same as NVDA)")]
				choices.extend(languages.native_name(code) for code in languages.available())
				self._codes = codes
				self.languageChoice = helper.addLabeledControl(
					strings.get("languageLabel", "Number &language:"),
					wx.Choice,
					choices=choices,
				)
				try:
					index = codes.index(plugin._languageSetting)
				except ValueError:
					index = 0
				self.languageChoice.SetSelection(index)

			def onSave(self):
				index = self.languageChoice.GetSelection()
				if 0 <= index < len(self._codes):
					plugin.setLanguageSetting(self._codes[index])

		try:
			NVDASettingsDialog.categoryClasses.append(LanguagePanel)
			self._settingsPanelClass = LanguagePanel
		except Exception:
			log.exception("Large Number Reader: could not register the settings panel")

	def _unregisterSettingsPanel(self):
		panel = self._settingsPanelClass
		if panel is None:
			return
		self._settingsPanelClass = None
		try:
			from gui.settingsDialogs import NVDASettingsDialog

			if panel in NVDASettingsDialog.categoryClasses:
				NVDASettingsDialog.categoryClasses.remove(panel)
		except Exception:
			log.exception("Large Number Reader: could not remove the settings panel")

	# --------------------------------------------------------------- speech

	def filterSpeechSequence(self, sequence):
		"""Rewrite large numbers in every piece of text NVDA is about to speak."""
		if not self._enabled or numberwords is None:
			return sequence
		try:
			if self._isCharacterMode(sequence):
				# Spelling or character by character reading: leave it alone.
				return sequence
			language = self._numberLanguage()
			changed = False
			result = []
			for item in sequence:
				if isinstance(item, str):
					newItem = numberwords.expand_text(item, language)
					if newItem != item:
						changed = True
					result.append(newItem)
				else:
					result.append(item)
			if not changed:
				return sequence
			return result
		except Exception:
			log.exception("Large Number Reader: filtering failed, speaking original text")
			return sequence

	@staticmethod
	def _isCharacterMode(sequence):
		characterMode = getattr(getattr(speech, "commands", None), "CharacterModeCommand", None)
		if characterMode is None:
			return False
		for item in sequence:
			if isinstance(item, characterMode) and getattr(item, "state", False):
				return True
		return False

	@scriptHandler.script(
		description="Turns reading of large numbers as words on and off",
		category=SCRIPT_CATEGORY,
	)
	def script_toggleNumberReading(self, gesture):
		self._enabled = not self._enabled
		try:
			config.conf[CONFIG_SECTION]["enabled"] = self._enabled
		except Exception:
			log.exception("Large Number Reader: could not save the setting")
		strings = self._strings()
		if self._enabled:
			ui.message(strings.get("readingOn", "Large number reading on"))
		else:
			ui.message(strings.get("readingOff", "Large number reading off"))

	__gestures = {
		"kb:NVDA+8": "toggleNumberReading",
	}
