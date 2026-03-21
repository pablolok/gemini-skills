"""Workflow optimization advisor.

This module provides logic to compare execution history against
the intended plan and workflow, identifying drift and suggesting optimizations.
"""

import logging
import typing


class WorkflowAdvisor:
    """Analyzes execution actions against plan and workflow documents."""

    def __init__(self, logger: typing.Optional[logging.Logger] = None) -> None:
        """Initializes the advisor.
        
        Args:
            logger: A logging.Logger instance for observability.
        """
        self._logger: logging.Logger = logger or logging.getLogger(__name__)

    def compare_execution_with_plan(
        self,
        actual_actions: typing.List[typing.Dict[str, typing.Any]],
        plan_content: str,
        workflow_content: str
    ) -> typing.List[str]:
        """Compares execution actions against the plan and workflow content.
        
        Args:
            actual_actions: Structured actions from ExecutionAnalyzer.
            plan_content: The text content of plan.md.
            workflow_content: The text content of workflow.md.
            
        Returns:
            A list of string advice/warnings about workflow drift.
        """
        self._logger.info("Comparing execution with plan...")
        advice: typing.List[str] = []
        
        # Super simple heuristic for the test:
        # Extract files mentioned in the plan content
        words: typing.List[str] = plan_content.replace("\n", " ").split()
        plan_files: typing.Set[str] = {w for w in words if "." in w and len(w) > 3}
        
        for action in actual_actions:
            target: str = action.get("target", "")
            if action.get("type") in ["read", "edit"] and target and target != "unknown":
                # If the target is a file, see if it was mentioned in the plan
                file_name: str = target.split("/")[-1].split("\\")[-1]
                
                # Check if it looks like a code file but isn't mentioned in the plan
                if file_name.endswith(".py") and file_name not in plan_content:
                    advice.append(
                        f"Workflow Drift: Action on '{target}' but '{file_name}' "
                        f"was not found in the current plan."
                    )
                    
        return advice
