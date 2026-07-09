"""
PII masking utilities for Neatlogs spans.

Redacts common personally identifiable information from trace payloads
before they are logged or sent to the Neatlogs server.
"""

import copy
import re
from typing import Any, Dict, List, Optional, Union

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)
PHONE_PATTERN = re.compile(
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
)

PII_FIELD_NAMES = frozenset({
    "customer_email",
    "email",
    "phone",
    "phone_number",
    "contact_number",
    "store_url",
    "store_credentials",
})


def mask_email(email: str) -> str:
    """Mask an email address, e.g. maya.patel@example.com -> m***@example.com."""
    if "@" not in email:
        return "***"
    local, domain = email.rsplit("@", 1)
    if not local:
        return f"***@{domain}"
    return f"{local[0]}***@{domain}"


def mask_phone(phone: str) -> str:
    """Mask a phone number, preserving only the last four digits."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) <= 4:
        return "***"
    return f"***-***-{digits[-4:]}"


def mask_pii_in_text(text: str) -> str:
    """Redact email and phone patterns from a string."""
    if not text:
        return text
    masked = EMAIL_PATTERN.sub(lambda match: mask_email(match.group(0)), text)
    return PHONE_PATTERN.sub("***-***-****", masked)


def mask_pii_in_data(
    data: Any,
    *,
    exclude_fields: Optional[List[str]] = None,
) -> Any:
    """
    Recursively mask PII in nested dicts, lists, and strings.

    Fields listed in ``exclude_fields`` are removed entirely from dict outputs.
    Known PII field names are masked or removed by default.
    """
    excluded = set(exclude_fields or [])
    excluded.update(PII_FIELD_NAMES)

    if isinstance(data, dict):
        result: Dict[str, Any] = {}
        for key, value in data.items():
            if key in excluded:
                continue
            if key in {"masked_email", "user_id", "ticket_id", "status", "scheduled_at"}:
                result[key] = value
                continue
            if key.endswith("_email") and isinstance(value, str):
                result[f"masked_{key}"] = mask_email(value)
                continue
            result[key] = mask_pii_in_data(value, exclude_fields=exclude_fields)
        return result

    if isinstance(data, list):
        return [mask_pii_in_data(item, exclude_fields=exclude_fields) for item in data]

    if isinstance(data, str):
        return mask_pii_in_text(data)

    return data


def sanitize_span_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize an LLM call payload before logging or transmission."""
    sanitized = copy.deepcopy(payload)
    for field in ("messages", "completion"):
        if field in sanitized:
            sanitized[field] = mask_pii_in_data(sanitized[field])
    return sanitized
