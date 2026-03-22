"""End-to-end test suite for the review_optimization skill."""

import logging
import typing
import unittest
from unittest.mock import MagicMock

from skills.review_optimization.analyzer import ExecutionAnalyzer
from skills.review_optimization.auditor import EfficiencyAuditor
from skills.review_optimization.advisor import WorkflowAdvisor
from skills.review_optimization.remediator import Remediator
from skills.review_optimization.proposer import SkillProposer


class TestReviewOptimizationE2E(unittest.TestCase):
    """End-to-end tests for the full optimization audit workflow."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.logger: logging.Logger = logging.getLogger("test_e2e")
        self.mock_ask_user: MagicMock = MagicMock()
        
        # Default mock response for generic questions (yesno/text)
        # For the new choice question, it needs to return a dict with the header key
        self.mock_ask_user.return_value = {
            "answers": {"0": "yes"},
            "New Skill Proposal": "Skip" # Default to skip for E2E
        }

        self.analyzer: ExecutionAnalyzer = ExecutionAnalyzer(self.logger)
        self.auditor: EfficiencyAuditor = EfficiencyAuditor(self.logger)
        self.advisor: WorkflowAdvisor = WorkflowAdvisor(self.logger)
        self.remediator: Remediator = Remediator(self.mock_ask_user, self.logger)
        self.proposer: SkillProposer = SkillProposer(self.mock_ask_user, self.logger)

    def test_full_workflow_with_findings(self) -> None:
        """Verify that the full workflow identifies and remediates multiple findings."""
        # Scenario: 
        # 1. User missed a skill (compliance-audit-scripts)
        # 2. User drifted from plan (edited a file not in plan)
        # 3. User used inefficient tools (cat/grep)
        # 4. User performed repetitive actions (ran script 3 times)
        
        history: typing.List[typing.Dict[str, typing.Any]] = [
            {"tool": "read_file", "args": {"file_path": "unplanned_file.py"}},
            {"tool": "replace", "args": {"file_path": "unplanned_file.py"}},
            {"tool": "run_shell_command", "args": {"command": "grep 'TODO' unplanned_file.py"}},
            {"tool": "run_shell_command", "args": {"command": "cat unplanned_file.py"}},
            {"tool": "run_shell_command", "args": {"command": "./repetitive.sh"}},
            {"tool": "run_shell_command", "args": {"command": "./repetitive.sh"}},
            {"tool": "run_shell_command", "args": {"command": "./repetitive.sh"}}
        ]
        
        available_skills: typing.List[typing.Dict[str, str]] = [
            {"name": "compliance-audit-scripts", "description": "Audit scripts"}
        ]
        
        plan_content: str = "## Phase 1\n- [ ] Task: Edit plan.md"
        workflow_content: str = "Standard workflow."

        # 1. Analyze
        actions: typing.List[typing.Dict[str, typing.Any]] = self.analyzer.parse_history(history)
        self.assertEqual(len(actions), 7)
        
        # 2. Audit for missed skills
        missed_skills: typing.List[typing.Dict[str, str]] = self.auditor.detect_missed_skills(actions, available_skills)
        self.assertIn("compliance-audit-scripts", [s["name"] for s in missed_skills])
        
        # 3. Advise on drift and tools
        drift: typing.List[str] = self.advisor.compare_execution_with_plan(actions, plan_content, workflow_content)
        self.assertTrue(any("unplanned_file.py" in d for d in drift))
        
        recommendations: typing.List[str] = self.advisor.recommend_tool_sequences(actions)
        self.assertTrue(any("grep_search" in r for r in recommendations))
        
        # 4. Remediate (Interactively)
        self.remediator.remediate_workflow_drift(drift)
        self.remediator.remediate_tool_usage(recommendations)
        
        # 5. Propose new skills
        self.proposer.analyze_for_new_skills(actions)
        
        # Verify that ask_user was called for each finding type
        # Drift (2: read and edit of unplanned_file.py), Tool Recs (2: grep and cat), Propose (1)
        # Total expected calls: 5
        self.assertEqual(self.mock_ask_user.call_count, 5)


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
