
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "ai-pipeline"))

from HITL_interface import get_human_decision


class TestHumanDecision(unittest.TestCase):

    def test_approve(self):
        with patch("builtins.input", side_effect=["1"]):
            decision, content = get_human_decision("Reviewed chapter")

        self.assertEqual(decision, "approve")
        self.assertEqual(content, "Reviewed chapter")

    def test_manual_edit(self):
        with patch(
            "builtins.input",
            side_effect=["2", "Edited chapter", "END"],
        ):
            decision, content = get_human_decision("Reviewed chapter")

        self.assertEqual(decision, "edit")
        self.assertEqual(content, "Edited chapter")

    def test_rewrite(self):
        with patch("builtins.input", side_effect=["3"]):
            decision, content = get_human_decision("Reviewed chapter")

        self.assertEqual(decision, "rewrite")
        self.assertEqual(content, "Reviewed chapter")

    def test_cancel(self):
        with patch("builtins.input", side_effect=["4"]):
            decision, content = get_human_decision("Reviewed chapter")

        self.assertEqual(decision, "cancel")
        self.assertEqual(content, "Reviewed chapter")

    def test_invalid_choice_then_approve(self):
        with patch("builtins.input", side_effect=["invalid", "1"]):
            decision, content = get_human_decision("Reviewed chapter")

        self.assertEqual(decision, "approve")
        self.assertEqual(content, "Reviewed chapter")


if __name__ == "__main__":
    unittest.main()
