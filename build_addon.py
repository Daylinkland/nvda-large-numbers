# -*- coding: utf-8 -*-
"""Generate the word list data files and build the .nvda-addon package.

Run:  python build_addon.py

The word files are generated so the add-on ships correct tables, but they are
plain text so anyone can fix a word their voice pronounces oddly.
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ADDON_DIR = os.path.join(ROOT, "addon")
PLUGIN_DIR = os.path.join(ADDON_DIR, "globalPlugins", "largeNumberReader")
DATA_DIR = os.path.join(PLUGIN_DIR, "data")

sys.path.insert(0, PLUGIN_DIR)
import languages  # noqa: E402


def read_manifest():
	values = {}
	with open(os.path.join(ADDON_DIR, "manifest.ini"), "r", encoding="utf-8") as handle:
		text = handle.read()
	# Simple key = value reader, enough for this manifest.
	for line in text.splitlines():
		if "=" in line and not line.lstrip().startswith(("#", ";")):
			key, _, value = line.partition("=")
			values[key.strip()] = value.strip().strip('"')
	return values


def _write_group_words(path, comment, builder):
	with open(path, "w", encoding="utf-8", newline="\n") as handle:
		handle.write(comment)
		handle.write("# Line number (starting at 0) is the number. Edit words here if a\n")
		handle.write("# voice pronounces something oddly. Keep exactly 1000 entries.\n")
		for number in range(1000):
			handle.write(builder(number) + "\n")


def _write_scales(path, comment, scales):
	with open(path, "w", encoding="utf-8", newline="\n") as handle:
		handle.write(comment)
		handle.write("# Line 1 is thousands, line 2 millions, and so on.\n")
		for scale in scales:
			handle.write(scale + "\n")


def write_data_files():
	os.makedirs(DATA_DIR, exist_ok=True)
	written = []

	english_groups = os.path.join(DATA_DIR, "number_words.txt")
	_write_group_words(
		english_groups,
		"# Large Number Reader: English words for 0 to 999, one per line.\n",
		languages.english_generated_group_word,
	)
	written.append(english_groups)

	english_scales = os.path.join(DATA_DIR, "scale_words.txt")
	_write_scales(
		english_scales,
		"# Large Number Reader: English scale names, smallest first.\n",
		languages.EN_SCALES,
	)
	written.append(english_scales)

	spanish_groups = os.path.join(DATA_DIR, "number_words_es.txt")
	_write_group_words(
		spanish_groups,
		"# Large Number Reader: Spanish words for 0 to 999, one per line.\n",
		languages.spanish_generated_group_word,
	)
	written.append(spanish_groups)

	spanish_scales = os.path.join(DATA_DIR, "scale_words_es.txt")
	_write_scales(
		spanish_scales,
		"# Large Number Reader: Spanish scale names (long scale), smallest first.\n",
		languages.ES_SCALES,
	)
	written.append(spanish_scales)

	return written


def build_package():
	manifest = read_manifest()
	version = manifest.get("version", "1.0")
	name = manifest.get("name", "largeNumberReader")
	out_path = os.path.join(ROOT, "%s-%s.nvda-addon" % (name, version))
	if os.path.exists(out_path):
		os.remove(out_path)

	with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
		for folder, _dirs, files in os.walk(ADDON_DIR):
			for file_name in sorted(files):
				if file_name.endswith((".pyc", ".pyo")) or "__pycache__" in folder:
					continue
				full = os.path.join(folder, file_name)
				rel = os.path.relpath(full, ADDON_DIR).replace("\\", "/")
				archive.write(full, rel)
	return out_path


def main():
	write_data_files()
	out_path = build_package()
	with zipfile.ZipFile(out_path) as archive:
		names = archive.namelist()
		if "manifest.ini" not in names:
			raise SystemExit("BUILD FAILED: manifest.ini is not at the root of the package")
		print("Package: %s" % out_path)
		print("Size:    %.1f KB" % (os.path.getsize(out_path) / 1024.0))
		print("Files:   %d" % len(names))
		total = 0
		for info in archive.infolist():
			print("  %7d  %s" % (info.file_size, info.filename))
			total += info.file_size
		print("Unpacked total: %.1f KB" % (total / 1024.0))


if __name__ == "__main__":
	main()
