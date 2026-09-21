"""Internationalization (i18n) helper for Hindi and English."""

import json
from pathlib import Path
from typing import Dict
import streamlit as st

I18N_DIR = Path(__file__).resolve().parent.parent / "i18n"


def load_translations() -> Dict[str, Dict[str, str]]:
    translations = {"en": {}, "hi": {}}
    en_file = I18N_DIR / "en.json"
    hi_file = I18N_DIR / "hi.json"

    if en_file.exists():
        with open(en_file, "r", encoding="utf-8") as f:
            translations["en"] = json.load(f)
    if hi_file.exists():
        with open(hi_file, "r", encoding="utf-8") as f:
            translations["hi"] = json.load(f)

    return translations


TRANSLATIONS = load_translations()


def get_current_language() -> str:
    """Returns the currently selected language code ('en' or 'hi')."""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    return st.session_state.lang


def t(key: str, default: str = "") -> str:
    """Translates a key into current language."""
    lang = get_current_language()
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS.get("en", {}).get(key, default or key))
