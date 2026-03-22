"""Interactive remediator for workflow and skill issues.

This module provides logic to construct interactive prompts for the user
to address findings from the optimization audit.
"""

import logging
import typing


class Remediator:
    """Orchestrates interactive remediation of detected issues."""

    def __init__(
        self,
        ask_user_fn: typing.Callable[
            [typing.List[typing.Dict[str, typing.Any]]],
            typing.Dict[str, typing.Any]
        ],
        logger: logging.Logger
    ) -> None:
        """Initializes the remediator.
        
        Args:
            ask_user_fn: A collaborator function to prompt the user.
            logger: A logging.Logger instance for observability.
        """
        if not callable(ask_user_fn):
            raise TypeError("ask_user_fn must be a callable")
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger instance")

        self._ask_user_fn: typing.Callable[
            [typing.List[typing.Dict[str, typing.Any]]],
            typing.Dict[str, typing.Any]
        ] = ask_user_fn
        self._logger: logging.Logger = logger

    def remediate_workflow_drift(self, findings: typing.List[str]) -> None:
        """Prompts the user to address workflow drift findings.
        
        Args:
            findings: A list of workflow drift findings.
        """
        if not isinstance(findings, list):
            raise TypeError("findings must be a list")

        if not findings:
            return

        self._logger.info(f"Remediating {len(findings)} workflow drift findings")
        
        for finding in findings:
            self._ask_user_fn([{
                "header": "Workflow Drift",
                "question": f"I detected the following drift: {finding}\n"
                            "Would you like to update the workflow or the plan to align with these actions?",
                "type": "yesno"
            }])

    def remediate_tool_usage(self, recommendations: typing.List[str]) -> None:
        """Prompts the user to address tool usage recommendations.
        
        Args:
            recommendations: A list of tool usage recommendations.
        """
        if not isinstance(recommendations, list):
            raise TypeError("recommendations must be a list")

        if not recommendations:
            return

        self._logger.info(f"Remediating {len(recommendations)} tool usage recommendations")
        
        for rec in recommendations:
            self._ask_user_fn([{
                "header": "Recommendation",
                "question": f"Optimization Opportunity: {rec}\n"
                            "Would you like me to follow this recommendation in future tasks?",
                "type": "yesno"
            }])
