"""Skill efficiency auditor for identifying missed or inefficient skill usage.

This module provides the EfficiencyAuditor class, which analyzes structured
actions to detect opportunities for skill usage and evaluate the performance
of activated skills.

Classes:
    EfficiencyAuditor: Analyze actions against available skills and patterns.
"""

import logging
import typing


class EfficiencyAuditor:
    """Analyze actions to detect missed or inefficiently used skills."""

    def __init__(self, logger: typing.Optional[logging.Logger] = None) -> None:
        """Initialize the auditor with an optional logger.
        
        Args:
            logger: A logging.Logger instance for observability.
        """
        self._logger: logging.Logger = logger or logging.getLogger(__name__)

    def detect_missed_skills(
        self,
        actions: typing.List[typing.Dict[str, typing.Any]],
        available_skills: typing.List[typing.Dict[str, str]]
    ) -> typing.List[typing.Dict[str, str]]:
        """Identify skills that were relevant but NOT activated.
        
        Args:
            actions: A list of structured actions taken in the session.
            available_skills: A list of available skills with name and desc.
            
        Returns:
            A list of missed skill definitions.
            
        Raises:
            TypeError: If input types are incorrect.
        """
        inputs_are_lists: bool = (
            isinstance(actions, list) and isinstance(available_skills, list)
        )
        if not inputs_are_lists:
            raise TypeError("Inputs must be lists")

        self._logger.info("Auditing for missed skills")
        missed: typing.List[typing.Dict[str, str]] = []
        
        # Simple keyword matching for demonstration.
        # In a real scenario, this would be more sophisticated.
        for skill in available_skills:
            name: str = skill.get("name", "").lower()
            desc: str = skill.get("description", "").lower()
            
            # Check if we ran shell commands that match skill keywords.
            for action in actions:
                if action.get("type") == "shell":
                    cmd: str = action.get("command", "").lower()
                    has_keyword: bool = (
                        "test" in name or "test" in desc or
                        "audit" in name or "audit" in desc
                    )
                    if has_keyword:
                        if "test" in cmd or "pytest" in cmd or "audit" in cmd or "grep" in cmd:
                            # If we ran tests/audits manually but didn't use the skill.
                            used_skill: bool = any(
                                a.get("type") == "skill" and
                                a.get("name") == skill.get("name")
                                for a in actions
                            )
                            if not used_skill:
                                missed.append(skill)
                                break
        return missed

    def evaluate_performance(
        self,
        actions: typing.List[typing.Dict[str, typing.Any]]
    ) -> typing.List[typing.Dict[str, str]]:
        """Evaluate if activated skills required manual corrections.
        
        Args:
            actions: A list of structured actions taken in the session.
            
        Returns:
            A list of skills that appeared inefficient.
            
        Raises:
            TypeError: If actions is not a list.
        """
        if not isinstance(actions, list):
            raise TypeError("actions must be a list")

        self._logger.info("Evaluating skill performance")
        inefficient: typing.List[typing.Dict[str, str]] = []
        
        for i, action in enumerate(actions):
            if action.get("type") == "skill":
                # Look for manual edits following a skill activation.
                if i + 1 < len(actions):
                    next_action: typing.Dict[str, typing.Any] = actions[i + 1]
                    if next_action.get("type") == "edit":
                        inefficient.append({
                            "name": str(action.get("name")),
                            "reason": "Manual edit followed skill activation"
                        })
        return inefficient
