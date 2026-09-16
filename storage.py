"""JSON persistence for contacts."""

import json
import os
from pathlib import Path
from typing import Any, cast


class StorageError(Exception):
    """Raised when contacts cannot be loaded or saved safely."""


STATE_FILE = ".contact_book_state.json"


def load_contacts(path: str | Path = "contacts.json") -> list[dict[str, Any]]:
    file_path = Path(path)

    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"The data file is invalid or corrupted: {error.msg}."
        ) from error
    except OSError as error:
        raise StorageError(f"Could not read the data file: {error}.") from error

    if not isinstance(raw_data, list):
        raise StorageError(
            "The data file must contain a JSON array of contact objects."
        )

    raw_items = cast(list[Any], raw_data)

    if any(not isinstance(item, dict) for item in raw_items):
        raise StorageError(
            "The data file must contain a JSON array of contact objects."
        )

    data = cast(list[dict[str, Any]], raw_items)
    contact_ids: set[int] = set()

    for contact in data:
        if "id" not in contact or "name" not in contact:
            raise StorageError(
                "Each contact must contain an id and a name."
            )

        contact_id = contact["id"]
        name = contact["name"]

        if (
            isinstance(contact_id, bool)
            or not isinstance(contact_id, int)
            or contact_id < 1
            or contact_id in contact_ids
            or not isinstance(name, str)
            or not name.strip()
            or any(
                key not in {"id", "name"} and not isinstance(value, str)
                for key, value in contact.items()
            )
        ):
            raise StorageError(
                "The data file contains an invalid contact record."
            )

        contact_ids.add(contact_id)

    return data


def load_next_id(
    contacts: list[dict[str, Any]],
    path: str | Path = STATE_FILE,
) -> int:
    file_path = Path(path)

    contact_ids = [
        contact["id"]
        for contact in contacts
        if isinstance(contact.get("id"), int)
        and not isinstance(contact.get("id"), bool)
    ]

    minimum_next_id = max(contact_ids, default=0) + 1

    if not file_path.exists():
        return minimum_next_id

    try:
        with file_path.open("r", encoding="utf-8") as file:
            stored_next_id = json.load(file)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"The ID state file is invalid or corrupted: {error.msg}."
        ) from error
    except OSError as error:
        raise StorageError(
            f"Could not read the ID state file: {error}."
        ) from error

    if (
        isinstance(stored_next_id, bool)
        or not isinstance(stored_next_id, int)
        or stored_next_id < 1
    ):
        raise StorageError("The ID state file contains an invalid next ID.")

    return max(stored_next_id, minimum_next_id)


def save_next_id(
    next_id: int,
    path: str | Path = STATE_FILE,
) -> None:
    if isinstance(next_id, bool) or next_id < 1:
        raise StorageError("The next ID must be a positive integer.")

    file_path = Path(path)
    temporary_path = file_path.with_name(f".{file_path.name}.tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(next_id, file)
            file.write("\n")

        os.replace(temporary_path, file_path)

    except (OSError, TypeError, ValueError) as error:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        raise StorageError(
            f"Could not save the ID state: {error}."
        ) from error


def save_contacts(
    contacts: list[dict[str, Any]],
    path: str | Path = "contacts.json",
) -> None:
    file_path = Path(path)
    temporary_path = file_path.with_name(f".{file_path.name}.tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(contacts, file, indent=4)
            file.write("\n")

        os.replace(temporary_path, file_path)

    except (OSError, TypeError, ValueError) as error:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        raise StorageError(
            f"Could not save the data file: {error}."
        ) from error