"""New skill proposer.

This module provides logic to detect recurring manual patterns in execution
history and propose the creation of new specialized skills.
"""

import collections
import logging
import typing


class SkillProposer:
    """Analyzes execution history to suggest new specialized skills."""

    def __init__(
        self,
        ask_user_fn: typing.Callable[[typing.List[typing.Dict[str, typing.Any]]], typing.Dict[str, typing.Any]],
        logger: logging.Logger
    ) -> None:
        """Initializes the proposer.
        
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

    def analyze_for_new_skills(
        self,
        actual_actions: typing.List[typing.Dict[str, typing.Any]],
        repetition_threshold: int = 3
    ) -> None:
        """Analyzes actions for recurring patterns and proposes new skills.
        
        Args:
            actual_actions: Structured actions from ExecutionAnalyzer.
            repetition_threshold: The number of occurrences to trigger a proposal.
        """
        if not isinstance(actual_actions, list):
            raise TypeError("actual_actions must be a list")

        self._logger.info("Analyzing for recurring patterns...")
        
        # Count shell commands
        shell_commands: typing.List[str] = [
            a.get("command", "") for a in actual_actions if a.get("type") == "shell"
        ]
        
        counts = collections.Counter(shell_commands)
        
        for cmd, count in counts.items():
            if count >= repetition_threshold and cmd:
                self._logger.info(f"Detected recurring pattern: '{cmd}' ({count} times)")
                self._ask_user_fn([{
                    "header": "New Skill Proposal",
                    "question": f"I detected a recurring pattern: you ran '{cmd}' {count} times.\n"
                                "Would you like to create a new specialized skill to automate this process?",
                    "type": "yesno"
                }])
