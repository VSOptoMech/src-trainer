"""Helpers for tolerant spoken-message matching."""

from __future__ import annotations

import re
import unicodedata

IGNORED_PHRASE_TOKENS = {"a", "an", "and", "the", "to"}


def phrase_matches_expected(actual: str, expected: str) -> bool:
    """Match spoken phrases by required content words, not exact punctuation or order."""
    expected_tokens = set(phrase_tokens(expected))
    actual_tokens = set(phrase_tokens(actual))
    return bool(expected_tokens) and expected_tokens <= actual_tokens


def phrase_tokens(value: str) -> list[str]:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return [
        token
        for token in re.findall(r"[a-z0-9]+", ascii_value.lower())
        if token not in IGNORED_PHRASE_TOKENS
    ]
