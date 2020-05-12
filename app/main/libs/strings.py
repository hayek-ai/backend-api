"""
libs2.strings

By default, uses `en-us.json` file inside the `strings` top-level folder.

If language changes, set `libs2.strings.default_locale` and run `libs2.strings.refresh()`.
"""
import json
import os

default_locale = "en-us"
cached_strings = {}


def refresh():
    print("Refreshing...")
    global cached_strings
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"../strings/{default_locale}.json")
    with open(filename) as f:
        cached_strings = json.load(f)


def get_text(name):
    return cached_strings[name]


refresh()
