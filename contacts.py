"""Business operations for a list of contact dictionaries."""

from typing import Any, TypeAlias

from validation import validate_field_name, validate_field_value, validate_name


Contact: TypeAlias = dict[str, Any]
Contacts: TypeAlias = list[Contact]

def find_by_id(contacts: Contacts, contact_id: int) -> Contact | None:
    return next(
        (contact for contact in contacts if contact.get("id") == contact_id),
        None,
    )


def find_duplicate(
    contacts: Contacts,
    name: str,
    fields: dict[str, str],
) -> Contact | None:
    normalized_fields = {
        key.casefold(): value.casefold()
        for key, value in fields.items()
    }

    for contact in contacts:
        contact_fields = {
            str(key).casefold(): str(value).casefold()
            for key, value in contact.items()
            if key not in {"id", "name"}
        }

        if contact_fields == normalized_fields:
            return contact

    return None


def add_contact(
    contacts: Contacts,
    contact_id: int,
    name: str,
    fields: dict[str, str],
) -> tuple[Contact, Contact | None]:

    clean_name = validate_name(name)

    clean_fields: dict[str, str] = {}

    for field_name, value in fields.items():
        clean_field_name = validate_field_name(field_name)
        clean_value = validate_field_value(value)

        if clean_field_name.casefold() in {
            key.casefold() for key in clean_fields
        }:
            raise ValueError(f"Duplicate field: '{clean_field_name}'.")

        clean_fields[clean_field_name] = clean_value

    duplicate = find_duplicate(contacts, clean_name, clean_fields)

    contact: Contact = {
        "id": contact_id,
        "name": clean_name,
        **clean_fields,
    }

    return contact, duplicate


def search_by_name(contacts: Contacts, query: str) -> Contacts:
    clean_query = query.strip()

    if not clean_query:
        return []

    lowered_query = clean_query.casefold()

    return [
        contact
        for contact in contacts
        if lowered_query in str(contact.get("name", "")).casefold()
    ]


def delete_by_id(contacts: Contacts, contact_id: int) -> Contact | None:
    contact = find_by_id(contacts, contact_id)

    if contact is None:
        return None

    contacts.remove(contact)
    return contact