"""Test suite for the interactive remediator."""

import logging
import typing
import unittest
from unittest.mock import MagicMock

import skills.review_optimization.remediator as remediator


class TestRemediator(unittest.TestCase):
    """Test suite for verifying the logic of the interactive remediator."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_ask_user: MagicMock = MagicMock()
        self.logger: logging.Logger = logging.getLogger("test_remediator")
        self.rem: remediator.Remediator = remediator.Remediator(
            self.mock_ask_user, self.logger
        )

    def test_prompt_for_workflow_drift(self) -> None:
        """Verify that the remediator prompts the user for workflow drift."""
        # Mocking ask_user to return a "yes" answer
        self.mock_ask_user.return_value = {"answers": {"0": "yes"}}

        findings: typing.List[str] = [
            "Workflow Drift: Action on 'user.py' but not in plan."
        ]

        # This should call ask_user
        self.rem.remediate_workflow_drift(findings)

        self.assertTrue(self.mock_ask_user.called)
        # Check the question in the first call
        call_args: typing.List[typing.Dict[str, typing.Any]] = (
            self.mock_ask_user.call_args[0][0]
        )
        self.assertIn("Workflow Drift", call_args[0]["question"])

    def test_prompt_for_tool_recommendations(self) -> None:
        """Verify that the remediator prompts for tool optimizations."""
        self.mock_ask_user.return_value = {"answers": {"0": "yes"}}

        recommendations: typing.List[str] = [
            "Recommendation: Use grep_search instead of grep."
        ]

        self.rem.remediate_tool_usage(recommendations)

        self.assertTrue(self.mock_ask_user.called)
        call_args: typing.List[typing.Dict[str, typing.Any]] = (
            self.mock_ask_user.call_args[0][0]
        )
        self.assertIn("Recommendation", call_args[0]["question"])

    def test_remediate_tool_usage_empty(self) -> None:
        """Verify that remediate_tool_usage does nothing when given empty input."""
        self.rem.remediate_tool_usage([])
        self.assertFalse(self.mock_ask_user.called)

    def test_remediate_workflow_drift_empty(self) -> None:
        """Verify that remediate_workflow_drift does nothing when given empty input."""
        self.rem.remediate_workflow_drift([])
        self.assertFalse(self.mock_ask_user.called)

    def test_init_invalid_args(self) -> None:
        """Verify that Remediator init raises TypeError for invalid arguments."""
        with self.assertRaisesRegex(TypeError, "ask_user_fn must be a callable"):
            remediator.Remediator(None, self.logger)  # type: ignore
        with self.assertRaisesRegex(TypeError, "logger must be a logging.Logger instance"):
            remediator.Remediator(self.mock_ask_user, None)  # type: ignore

    def test_remediate_methods_invalid_args(self) -> None:
        """Verify that Remediator methods raise TypeError for invalid arguments."""
        with self.assertRaisesRegex(TypeError, "findings must be a list"):
            self.rem.remediate_workflow_drift(None)  # type: ignore
        with self.assertRaisesRegex(TypeError, "recommendations must be a list"):
            self.rem.remediate_tool_usage(None)  # type: ignore


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
