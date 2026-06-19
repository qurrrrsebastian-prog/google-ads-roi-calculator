"""Security utilities for Google Ads ROI Calculator — Emerald Fortune.

Provides input sanitization, validation, session ID generation and API key
masking. All functions are defensive and never raise unexpected exceptions to
the UI layer beyond the documented ValueError cases.
"""
from __future__ import annotations

import re
import uuid

# Forbidden SQL keywords — block destructive / injection attempts in free text.
_SQL_BLOCKLIST = re.compile(
    r"\b(drop|delete|alter|insert|update|truncate|exec|union\s+select)\b",
    re.IGNORECASE,
)

# Allowed characters for free-text input after HTML stripping.
_ALLOWED_CHARS = re.compile(r"[^a-zA-Z0-9\s.,!?()\-]")

# HTML / script tag matcher.
_HTML_TAG = re.compile(r"<[^>]*>")

_MAX_LEN = 500


def sanitize_input(text: str) -> str:
    """Strip HTML tags, block scripts/SQL, keep safe chars, limit to 500.

    Returns a cleaned string. Empty/invalid input becomes "".
    """
    if text is None:
        return ""
    try:
        s = str(text)
    except Exception:
        return ""

    # Hard block obvious script content and SQL injection attempts.
    if "<script" in s.lower() or _SQL_BLOCKLIST.search(s):
        # Remove the offending content rather than echoing it back.
        s = _SQL_BLOCKLIST.sub("", s)
        s = re.sub(r"<\s*script.*?>.*?<\s*/\s*script\s*>", "", s,
                   flags=re.IGNORECASE | re.DOTALL)

    s = _HTML_TAG.sub("", s)            # strip any remaining tags
    s = _ALLOWED_CHARS.sub("", s)       # whitelist characters
    s = s.strip()
    return s[:_MAX_LEN]


def validate_numeric(value, min_val: float = 0, max_val: float = 999_999_999) -> float:
    """Validate a numeric value is a number within (min_val, max_val].

    Raises ValueError if not a valid float/int, <= min_val, or > max_val.
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Nilai '{value}' bukan angka yang valid.")

    if num != num or num in (float("inf"), float("-inf")):  # NaN / inf guard
        raise ValueError("Nilai numerik tidak valid (NaN/inf).")
    if num <= min_val:
        raise ValueError(f"Nilai harus lebih besar dari {min_val}.")
    if num > max_val:
        raise ValueError(f"Nilai melebihi maksimum {max_val:,.0f}.")
    return num


def validate_select(value: str, options: list) -> str:
    """Ensure value exists in the allowed options list (prevent injection)."""
    if value not in options:
        raise ValueError(f"Pilihan '{value}' tidak valid.")
    return value


def generate_session_id() -> str:
    """Return an 8-char hex session id."""
    return uuid.uuid4().hex[:8]


def mask_api_key(key: str) -> str:
    """Mask an API key, showing only first 4 and last 4 characters."""
    if not key:
        return "****"
    key = str(key)
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}****{key[-4:]}"


def format_rupiah(value) -> str:
    """Format a number as Rupiah with thousand separators. Safe on bad input."""
    try:
        return f"Rp {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Rp 0"
