# Contact Book

## Description

A standalone Python command-line contact book. Each contact has a system-assigned ID, a required name, and one or more user-defined fields. Contacts are held in memory as a list of dictionaries and saved as JSON.

## Features

- Add, view, search, select, and delete contacts through dot-style commands
- Store arbitrary custom fields such as `phone`, `email`, `address`, `website`, or `company`
- Use persistent integer IDs that are never reused, including after deletion and restart
- Search names with a case-insensitive partial match
- Allow duplicate names while detecting duplicate contacts from their complete custom-field mapping
- Handle invalid input, file errors, and corrupted data files with clear messages

## Requirements

- Python 3.10 or newer
- No third-party packages

## Installation

Run the application from this directory:

```text
python main.py
```

## Usage

```text
add.<name>, <field>:<value>, ...
view
view.<id>
search.<query>
select.<id>
delete.<id>
help
exit
```

`add` requires a name and at least one custom field.; `add.<name>` alone is invalid. Field names may contain letters, numbers, spaces, and underscores, but `id` and `name` are reserved. Field names are compared case-insensitively, so a contact cannot contain both `phone` and `Phone`.

Custom field values are general non-empty strings; the application does not apply phone- or email-specific validation. To include a comma in a value, wrap that value in double quotes.

Duplicate detection ignores the contact name and compares every custom field name and value case-insensitively. When a duplicate is found, the application displays the existing contact and asks whether to add the new one anyway.

`view` and `search` display each contact's persistent ID. `view.<id>` and `select.<id>` display all contact fields except the internal ID. `delete.<id>` always asks for confirmation before removing a contact.

Examples:

```text
add.Ramesh Sharma, phone:+91 9831019372, email:ramesh@example.com
add.Alice, city:Kolkata, website:https://example.com
add.Ramesh, address:"12, Park Street, Kolkata", city:Kolkata
search.Ramesh
view.1
```

## Data Persistence

- `contacts.json` stores the contact records as a JSON array.
- `.contact_book_state.json` stores the next available ID so deleted IDs are never reused.

Successful additions and deletions are saved immediately. A missing contact file starts an empty contact book. Invalid JSON is reported without overwriting the existing file.

## Project Structure

- `main.py`: command-line interface, command parsing, and user interaction
- `contacts.py`: contact operations, duplicate detection, searching, and deletion
- `validation.py`: name, custom field-name, and custom field-value validation
- `storage.py`: JSON loading/saving and persistent ID state
- `tests/`: automated behavior tests

## Error Handling

Malformed commands, invalid fields, duplicate field names, invalid IDs, invalid confirmations, file errors, and corrupted JSON are handled without normal-flow tracebacks.
