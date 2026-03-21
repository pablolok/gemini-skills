"""Test suite for the workflow optimization advisor."""

import typing
import unittest

# Using try/except to allow tests to fail gracefully during Red Phase TDD
try:
    import skills.review_optimization.advisor as advisor
except ImportError:
    advisor = None  # type: ignore


class TestWorkflowAdvisor(unittest.TestCase):
    """Test suite for verifying the logic of the workflow advisor."""

    def test_compare_execution_with_plan_detects_drift(self) -> None:
        """Verify that the advisor detects when actions deviate from the plan."""
        if advisor is None:
            self.fail("advisor module not implemented yet")
            
        workflow_advisor: 'advisor.WorkflowAdvisor' = advisor.WorkflowAdvisor()
        
        actual_actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "read", "target": "some_random_file.py"},
            {"type": "edit", "target": "some_random_file.py"}
        ]
        
        plan_content: str = "## Phase 1\n- [~] Task: Implement user model in user.py"
        workflow_content: str = "Standard workflow requires updating user.py"
        
        advice: typing.List[str] = workflow_advisor.compare_execution_with_plan(
            actual_actions, plan_content, workflow_content
        )
        
        # We expect the advisor to flag that 'some_random_file.py' was edited
        # but the plan mentions 'user.py'.
        self.assertTrue(len(advice) > 0)
        self.assertTrue(any("drift" in msg.lower() or "deviation" in msg.lower() for msg in advice))

    def test_compare_execution_no_drift(self) -> None:
        """Verify that the advisor reports no issues when execution matches plan."""
        if advisor is None:
            self.fail("advisor module not implemented yet")
            
        workflow_advisor: 'advisor.WorkflowAdvisor' = advisor.WorkflowAdvisor()
        
        actual_actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "read", "target": "user.py"},
            {"type": "edit", "target": "user.py"}
        ]
        
        plan_content: str = "## Phase 1\n- [~] Task: Implement user model in user.py"
        workflow_content: str = "Standard workflow requires updating user.py"
        
        advice: typing.List[str] = workflow_advisor.compare_execution_with_plan(
            actual_actions, plan_content, workflow_content
        )
        
        # Should not flag anything if the actions are aligned with the plan.
        self.assertEqual(len(advice), 0)

    def test_recommend_tool_sequences(self) -> None:
        """Verify that the advisor suggests better tool sequences for inefficient actions."""
        if advisor is None:
            self.fail("advisor module not implemented yet")
            
        workflow_advisor: 'advisor.WorkflowAdvisor' = advisor.WorkflowAdvisor()
        
        # Suppose a user runs grep inside a bash shell instead of using grep_search
        inefficient_actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "shell", "command": "grep 'TODO' src/app.py"},
            {"type": "shell", "command": "cat src/app.py"}
        ]
        
        recommendations: typing.List[str] = workflow_advisor.recommend_tool_sequences(
            inefficient_actions
        )
        
        self.assertTrue(len(recommendations) >= 2)
        self.assertTrue(any("grep_search" in msg for msg in recommendations))
        self.assertTrue(any("read_file" in msg for msg in recommendations))


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
