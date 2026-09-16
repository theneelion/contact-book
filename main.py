from __future__ import annotations

from typing import Any, TypeAlias

from contacts import add_contact, delete_by_id, find_by_id, search_by_name
from storage import (
    StorageError,
    load_contacts,
    load_next_id,
    save_contacts,
    save_next_id,
)


Contact: TypeAlias = dict[str, Any]
Contacts: TypeAlias = list[Contact]

DATA_FILE = "contacts.json"


def print_details(contact: Contact) -> None:
    for key, value in contact.items():
        if key != "id":
            print(f"{key.title()} : {value}")


def print_compact(contacts: Contacts) -> None:
    for contact in contacts:
        print(f"ID: {contact['id']} | {contact['name']}")


def parse_id(value: str) -> int | None:
    try:
        contact_id = int(value.strip())
    except ValueError:
        return None
    return contact_id if contact_id > 0 else None


def show_contact(contacts: Contacts, raw_id: str) -> None:
    contact_id = parse_id(raw_id)
    if contact_id is None:
        print("Invalid ID. Enter a positive integer.")
        return
    contact = find_by_id(contacts, contact_id)
    if contact is None:
        print(f"Contact with ID {contact_id} not found.")
        return
    print_details(contact)

def parse_add_argument(argument: str) -> tuple[str, dict[str, str]]:
    parts: list[str] = []
    current: list[str] = []
    in_quotes = False

    for char in argument:
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if in_quotes:
        raise ValueError("Unclosed quotation mark.")

    parts.append("".join(current).strip())

    if len(parts) < 2:
        raise ValueError("Usage: add.<name>, <field>:<value>, ...")

    name = parts[0]
    fields: dict[str, str] = {}

    for part in parts[1:]:
        if ":" not in part:
            raise ValueError("Each field must use the format <field>:<value>.")

        field_name, value = part.split(":", 1)
        field_name = field_name.strip()
        value = value.strip()

        if field_name.casefold() in {key.casefold() for key in fields}:
            raise ValueError(f"Duplicate field: '{field_name}'.")

        fields[field_name] = value

    return name, fields

def handle_add(contacts: Contacts, argument: str) -> None:
    try:
        name, fields = parse_add_argument(argument)
    except ValueError as error:
        print(error)
        return

    try:
        next_contact_id = load_next_id(contacts)
        contact, duplicate = add_contact(
            contacts,
            next_contact_id,
            name,
            fields,
        )
    except (StorageError, ValueError) as error:
        print(error)
        return

    if duplicate is not None:
        print("Duplicate contact found.")
        print("\nExisting contact:")
        print_details(duplicate)

        answer = input("\nAdd this contact anyway? [y/n]: ").strip().casefold()

        if answer == "n":
            print("Contact was not added.")
            return

        if answer != "y":
            print("Invalid response. Enter 'y' or 'n'.")
            return

    try:
        save_next_id(next_contact_id + 1)
    except StorageError as error:
        print(error)
        return

    contacts.append(contact)

    try:
        save_contacts(contacts, DATA_FILE)
    except StorageError as error:
        contacts.remove(contact)
        print(error)
        return

    print(f"Contact added successfully. ID: {contact['id']}")


def handle_view(contacts: Contacts, argument: str | None) -> None:
    if argument is not None:
        show_contact(contacts, argument)
        return
    if not contacts:
        print("No contacts found.")
        return
    print("Contacts:\n")
    print_compact(contacts)


def handle_search(contacts: Contacts, query: str) -> None:
    clean_query = query.strip()
    if not clean_query:
        print("Search query cannot be empty.")
        return
    matches = search_by_name(contacts, clean_query)
    if not matches:
        print(f'No contacts found for "{clean_query}".')
        return
    print("Search Results:\n")
    print_compact(matches)


def handle_delete(contacts: Contacts, raw_id: str) -> None:
    contact_id = parse_id(raw_id)
    if contact_id is None:
        print("Invalid ID. Enter a positive integer.")
        return
    contact = find_by_id(contacts, contact_id)
    if contact is None:
        print(f"Contact with ID {contact_id} not found.")
        return
    contact_index = contacts.index(contact)
    print("Contact:\n")
    print_details(contact)
    answer = input("\nDelete this contact? [y/n]: ").strip().casefold()
    if answer == "n":
        print("Deletion cancelled.")
        return
    if answer != "y":
        print("Invalid response. Enter 'y' or 'n'.")
        return
    delete_by_id(contacts, contact_id)
    try:
        save_contacts(contacts, DATA_FILE)
    except StorageError as error:
        contacts.insert(contact_index, contact)
        print(error)
        return
    print("Contact deleted successfully.")


def print_help() -> None:
    print("""Available Commands:

add.<name>, <field>:<value>, ...
    Add a new contact.

view
    View all contacts.

view.<id>
    View one contact's details.

search.<query>
    Search contacts by name.

select.<id>
    Display one contact's details.

delete.<id>
    Delete a contact after confirmation.

help
    Show available commands.

exit
    Exit the application.""")


def run() -> None:
    try:
        contacts = load_contacts(DATA_FILE)
    except StorageError as error:
        print(error)
        return

    print("Contact Book")
    print("Type 'help' to see available commands.")
    while True:
        try:
            command = input("\n> ").strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        if not command:
            print("Please enter a command. Type 'help' for assistance.")
            continue
        if command == "exit":
            print("Goodbye.")
            break
        if command == "help":
            print_help()
            continue
        if command == "view":
            handle_view(contacts, None)
            continue
        if command.startswith("add."):
            handle_add(contacts, command[4:])
            continue
        if command.startswith("view."):
            handle_view(contacts, command[5:])
            continue
        if command.startswith("search."):
            handle_search(contacts, command[7:])
            continue
        if command.startswith("select."):
            show_contact(contacts, command[7:])
            continue
        if command.startswith("delete."):
            handle_delete(contacts, command[7:])
            continue
        print("Unknown command. Type 'help' to see available commands.")


if __name__ == "__main__":
    run()
