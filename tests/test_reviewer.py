import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "ai-pipeline"))

from reviewer import review_text_with_llama, check_source_fidelity

class TestReviewer(unittest.TestCase):
    
    @patch("reviewer.get_groq_client")
    def test_fidelity_checker_sends_source_and_draft(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        response = MagicMock()
        response.choices[0].message.content = "FLAG: A source event is missing."
        client.chat.completions.create.return_value = response

        result = check_source_fidelity("Original chapter.", "Draft chapter.")

        self.assertEqual(result, "FLAG: A source event is missing.")

        messages = client.chat.completions.create.call_args.kwargs["messages"]
        user_message = messages[1]["content"]

        self.assertIn("Original chapter.", user_message)
        self.assertIn("Draft chapter.", user_message)

    @patch("reviewer.get_groq_client")
    def test_reviewer_sends_original_and_draft_to_model(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        response = MagicMock()
        response.choices[0].message.content = "Revised chapter."
        client.chat.completions.create.return_value = response

        result = review_text_with_llama(
            "Original chapter.",
            "Draft chapter.",
        )

        self.assertEqual(result, "Revised chapter.")

        messages = client.chat.completions.create.call_args.kwargs["messages"]
        user_message = messages[1]["content"]

        self.assertIn("Original chapter.", user_message)
        self.assertIn("Draft chapter.", user_message)

    def test_empty_original_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Original chapter cannot be empty"):
            review_text_with_llama("", "Draft chapter.")

    def test_empty_draft_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Text to review cannot be empty"):
            review_text_with_llama("Original chapter.", "  ")

    @patch("reviewer.get_groq_client")
    def test_check_source_fidelity_sends_original_and_draft_to_model(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        response = MagicMock()
        response.choices[0].message.content = "PASS"
        client.chat.completions.create.return_value = response

        result = check_source_fidelity(
            "Original chapter.",
            "Draft chapter.",
        )

        self.assertEqual(result, "PASS")

        messages = client.chat.completions.create.call_args.kwargs["messages"]
        user_message = messages[1]["content"]

        self.assertIn("Original chapter.", user_message)
        self.assertIn("Draft chapter.", user_message)

    def test_check_source_fidelity_rejects_empty_original(self):
        with self.assertRaisesRegex(ValueError, "Original chapter cannot be empty"):
            check_source_fidelity("", "Draft chapter.")

    def test_check_source_fidelity_rejects_empty_draft(self):
        with self.assertRaisesRegex(ValueError, "Draft chapter cannot be empty"):
            check_source_fidelity("Original chapter.", "  ")


if __name__ == "__main__":
    unittest.main()