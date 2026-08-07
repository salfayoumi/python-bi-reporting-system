"""
modules/i18n.py

Central translation loader for English and Turkish support.

User-facing strings live in locales/en.json and locales/tr.json.
The loader rejects duplicate JSON keys and verifies language-key parity
at import time so translation drift fails loudly during development.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SUPPORTED_LANGUAGES = ("en", "tr")
DEFAULT_LANGUAGE = "en"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = PROJECT_ROOT / "locales"


def _reject_duplicate_keys(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    """Build a dict while rejecting duplicate JSON object keys."""

    result: dict[str, Any] = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                f"Duplicate translation key found: {key!r}"
            )
        result[key] = value

    return result


def _load_language(
    language: str,
) -> dict[str, str]:
    """Load and validate one language file."""

    path = LOCALES_DIR / f"{language}.json"

    if not path.is_file():
        raise ValueError(
            f"Translation file is missing: {path}"
        )

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Translation file is invalid JSON: {path}"
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            f"Translation file must contain a JSON object: {path}"
        )

    invalid_values = [
        key
        for key, value in data.items()
        if not isinstance(value, str)
    ]

    if invalid_values:
        raise ValueError(
            "All translation values must be strings. "
            f"Invalid keys: {invalid_values}"
        )

    return data


TRANSLATIONS = {
    language: _load_language(language)
    for language in SUPPORTED_LANGUAGES
}

_language_key_sets = {
    language: set(values)
    for language, values in TRANSLATIONS.items()
}

if len(set(map(frozenset, _language_key_sets.values()))) != 1:
    raise ValueError(
        "Translation key parity check failed between languages."
    )


def normalize_language(language: str) -> str:
    """Return a supported language code."""

    if not isinstance(language, str):
        return DEFAULT_LANGUAGE

    normalized = language.lower().strip()

    if normalized not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE

    return normalized


def translate(
    key: str,
    language: str = DEFAULT_LANGUAGE,
    **kwargs: Any,
) -> str:
    """
    Return a localized string and format it with supplied parameters.

    Missing language-specific keys fall back to English; unknown keys
    fall back to the key name itself. Formatting errors are never hidden.
    """

    selected_language = normalize_language(language)

    text = TRANSLATIONS[selected_language].get(
        key,
        TRANSLATIONS[DEFAULT_LANGUAGE].get(
            key,
            key,
        ),
    )

    try:
        return text.format(**kwargs)
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError(
            f"Translation formatting failed for key {key!r} "
            f"and language {language!r}."
        ) from error
