import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from typing import Any

Contact = dict[str, Any]
Contacts = list[Contact]

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from contacts import add_contact, delete_by_id, search_by_name
from main import handle_add, handle_delete
from storage import StorageError, load_contacts, save_contacts
from validation import validate_field_name, validate_field_value, validate_name


class ContactBookTests(unittest.TestCase):

    def test_validation_trims_and_rejects_invalid_values(self):
        self.assertEqual(
            validate_name("  Ramesh Sharma  "),
            "Ramesh Sharma",
        )

        self.assertEqual(
            validate_field_name("  Github  "),
            "Github",
        )

        self.assertEqual(
            validate_field_value("  testuser  "),
            "testuser",
        )

        for value in ("", "   "):
            with self.assertRaises(ValueError):
                validate_name(value)

        for value in ("", "   "):
            with self.assertRaises(ValueError):
                validate_field_name(value)

        for value in ("", "   "):
            with self.assertRaises(ValueError):
                validate_field_value(value)

    def test_duplicate_names_are_allowed_but_same_fields_are_detected(self):
        contacts: list[dict[str, Any]] = []

        first, duplicate = add_contact(
            contacts,
            1,
            "Ramesh Sharma",
            {
                "phone": "9831667002",
                "email": "ramesh@example.com",
            },
        )

        self.assertIsNone(duplicate)
        contacts.append(first)

        second, duplicate = add_contact(
            contacts,
            2,
            "Ramesh Sharma",
            {
                "phone": "9831667999",
                "email": "other@example.com",
            },
        )

        self.assertIsNone(duplicate)
        contacts.append(second)

        third, duplicate = add_contact(
            contacts,
            3,
            "Other Name",
            {
                "phone": "9831667002",
                "email": "ramesh@example.com",
            },
        )

        self.assertEqual(duplicate, first)
        self.assertEqual(third["id"], 3)

    def test_search_is_case_insensitive_and_preserves_ids(self):
        contacts: Contacts = [
            {
                "id": 4,
                "name": "Ramesh Sharma",
                "phone": "1234567",
                "email": "a@example.com",
            },
            {
                "id": 9,
                "name": "Rahul Sen",
                "phone": "1234568",
                "email": "b@example.com",
            },
        ]

        self.assertEqual(
            [contact["id"] for contact in search_by_name(contacts, "SHAR")],
            [4],
        )

        self.assertEqual(
            search_by_name(contacts, "   "),
            [],
        )

    def test_delete_does_not_reuse_ids(self):
        contacts: Contacts = [
            {
                "id": 1,
                "name": "A",
                "phone": "1234567",
                "email": "a@example.com",
            },
            {
                "id": 2,
                "name": "B",
                "phone": "1234568",
                "email": "b@example.com",
            },
        ]

        delete_by_id(contacts, 1)

        new_contact, _ = add_contact(
            contacts,
            3,
            "C",
            {
                "phone": "1234569",
                "email": "c@example.com",
            },
        )

        self.assertEqual(new_contact["id"], 3)

    def test_duplicate_confirmation_requires_y_or_n(self):
        contacts: Contacts = [
            {
                "id": 1,
                "name": "Existing",
                "phone": "1234567",
                "email": "a@example.com",
            }
        ]

        with (
            patch("main.input", return_value="maybe"),
            patch("main.load_next_id", return_value=2),
            patch("main.save_next_id"),
            patch("main.save_contacts"),
        ):
            handle_add(
                contacts,
                "New Name, phone:1234567, email:a@example.com",
            )

        self.assertEqual(len(contacts), 1)

    def test_delete_confirmation(self):
        contacts: Contacts = [
            {
                "id": 1,
                "name": "Existing",
                "phone": "1234567",
                "email": "a@example.com",
            }
        ]

        with patch("main.input", return_value="n"):
            handle_delete(contacts, "1")

        self.assertEqual(len(contacts), 1)

    def test_storage_round_trip_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contacts.json"

            original: Contacts = [
                {
                    "id": 7,
                    "name": "Example",
                    "phone": "1234567",
                    "email": "e@example.com",
                }
            ]

            save_contacts(original, path)

            self.assertEqual(
                load_contacts(path),
                original,
            )

            path.write_text(
                "{not json",
                encoding="utf-8",
            )

            with self.assertRaises(StorageError):
                load_contacts(path)

            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "{not json",
            )

    def test_cli_persists_add_and_delete_across_restarts(self):
        with tempfile.TemporaryDirectory() as directory:
            data_path = Path(directory) / "contacts.json"

            data_path.write_text(
                "[]\n",
                encoding="utf-8",
            )

            add = subprocess.run(
                [sys.executable, str(ROOT / "main.py")],
                input=(
                    "add.Example Person, "
                    "phone:1234567, "
                    "email:example@example.com\n"
                    "exit\n"
                ),
                text=True,
                capture_output=True,
                cwd=directory,
                check=True,
            )

            self.assertIn(
                "Contact added successfully. ID: 1",
                add.stdout,
            )

            view = subprocess.run(
                [sys.executable, str(ROOT / "main.py")],
                input="view\nexit\n",
                text=True,
                capture_output=True,
                cwd=directory,
                check=True,
            )

            self.assertIn(
                "ID: 1 | Example Person",
                view.stdout,
            )

            delete = subprocess.run(
                [sys.executable, str(ROOT / "main.py")],
                input="delete.1\ny\nexit\n",
                text=True,
                capture_output=True,
                cwd=directory,
                check=True,
            )

            self.assertIn(
                "Contact deleted successfully.",
                delete.stdout,
            )

            self.assertEqual(
                json.loads(
                    data_path.read_text(encoding="utf-8")
                ),
                [],
            )


if __name__ == "__main__":
    unittest.main()