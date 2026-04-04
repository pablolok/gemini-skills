"""Test suite for the skill efficiency auditor."""

import os
import typing
import unittest

import importlib
auditor = importlib.import_module("skills.review-optimization.auditor")


class TestEfficiencyAuditor(unittest.TestCase):
    """Test suite for verifying the logic of the skill efficiency auditor."""

    def test_detect_missed_skills(self) -> None:
        """Verify that the auditor can detect missed skill opportunities."""
        audit: auditor.EfficiencyAuditor = auditor.EfficiencyAuditor()
        # Mock actions where we manually run tests instead of using a skill.
        actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "shell", "command": "npm test"},
            {"type": "shell", "command": "python3 -m unittest"}
        ]
        # Available skills that could have been used.
        available_skills: typing.List[typing.Dict[str, str]] = [
            {
                "name": "test-runner",
                "description": "Runs tests for the project"
            }
        ]
        missed: typing.List[typing.Dict[str, str]] = audit.detect_missed_skills(
            actions, available_skills
        )
        self.assertGreater(len(missed), 0)
        self.assertEqual(missed[0]["name"], "test-runner")

    def test_detect_missed_skills_invalid_input(self) -> None:
        """Verify that detect_missed_skills raises TypeError for invalid input."""
        audit: auditor.EfficiencyAuditor = auditor.EfficiencyAuditor()
        with self.assertRaises(TypeError):
            audit.detect_missed_skills(None, [])  # type: ignore

    def test_evaluate_skill_performance(self) -> None:
        """Verify that the auditor can evaluate how skills performed."""
        audit: auditor.EfficiencyAuditor = auditor.EfficiencyAuditor()
        # Mock actions where a skill was used but followed by manual corrections
        # using a platform-agnostic path.
        actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "skill", "name": "code-fixer"},
            {"type": "edit", "target": os.path.join("src", "app.js")}
        ]
        inefficient: typing.List[typing.Dict[str, str]] = audit.evaluate_performance(
            actions
        )
        self.assertGreater(len(inefficient), 0)
        self.assertEqual(inefficient[0]["name"], "code-fixer")

    def test_evaluate_performance_invalid_input(self) -> None:
        """Verify that evaluate_performance raises TypeError for invalid input."""
        audit: auditor.EfficiencyAuditor = auditor.EfficiencyAuditor()
        with self.assertRaises(TypeError):
            audit.evaluate_performance("not a list")  # type: ignore


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
