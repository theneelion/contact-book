"""Input validation for contact data."""

import re


FIELD_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_ ]+$")


def validate_name(name: str) -> str:
    value = name.strip()

    if not value:
        raise ValueError("Name cannot be empty.")

    return value


def validate_field_name(field_name: str) -> str:
    value = field_name.strip()

    if not value:
        raise ValueError("Field name cannot be empty.")

    if value.casefold() in {"id", "name"}:
        raise ValueError("'id' and 'name' are reserved fields.")

    if not FIELD_NAME_PATTERN.fullmatch(value):
        raise ValueError(
            "Field names may contain letters, numbers, spaces, and underscores."
        )

    return value


def validate_field_value(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("Field value cannot be empty.")

    return value