"""Test suite for the new skill proposer."""

import logging
import typing
import unittest
from unittest.mock import MagicMock

import skills.review_optimization.proposer as proposer


class TestSkillProposer(unittest.TestCase):
    """Test suite for verifying the logic of the skill proposer."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_ask_user = MagicMock()
        self.logger: logging.Logger = logging.getLogger("test_proposer")

    def test_propose_new_skill_detects_recurring_shell_commands(self) -> None:
        """Verify that the proposer detects recurring shell commands and suggests a skill."""
        skill_proposer: proposer.SkillProposer = proposer.SkillProposer(
            self.mock_ask_user, self.logger
        )
        
        # Scenario: User runs the same custom script/command 3 times
        repetitive_actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "shell", "command": "./my_custom_task.sh"},
            {"type": "shell", "command": "./my_custom_task.sh"},
            {"type": "shell", "command": "./my_custom_task.sh"}
        ]
        
        # This should call ask_user once to propose a new skill
        skill_proposer.analyze_for_new_skills(repetitive_actions)
        
        self.assertTrue(self.mock_ask_user.called)
        call_args = self.mock_ask_user.call_args[0][0]
        self.assertIn("recurring pattern", call_args[0]["question"].lower())
        self.assertIn("./my_custom_task.sh", call_args[0]["question"])

    def test_no_proposal_for_non_repetitive_actions(self) -> None:
        """Verify that the proposer does not suggest a skill for unique actions."""
        skill_proposer: proposer.SkillProposer = proposer.SkillProposer(
            self.mock_ask_user, self.logger
        )
        
        unique_actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "shell", "command": "npm test"},
            {"type": "shell", "command": "git status"},
            {"type": "shell", "command": "ls"}
        ]
        
        skill_proposer.analyze_for_new_skills(unique_actions)
        
        self.assertFalse(self.mock_ask_user.called)

    def test_init_invalid_args(self) -> None:
        """Verify that SkillProposer init raises TypeError for invalid arguments."""
        with self.assertRaisesRegex(TypeError, "ask_user_fn must be a callable"):
            proposer.SkillProposer(None, self.logger)  # type: ignore
        with self.assertRaisesRegex(TypeError, "logger must be a logging.Logger instance"):
            proposer.SkillProposer(self.mock_ask_user, None)  # type: ignore

    def test_analyze_invalid_args(self) -> None:
        """Verify that analyze_for_new_skills raises TypeError for invalid arguments."""
        skill_proposer: proposer.SkillProposer = proposer.SkillProposer(
            self.mock_ask_user, self.logger
        )
        with self.assertRaisesRegex(TypeError, "actual_actions must be a list"):
            skill_proposer.analyze_for_new_skills(None)  # type: ignore


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
