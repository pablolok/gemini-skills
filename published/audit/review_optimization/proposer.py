"""New skill proposer.

This module provides logic to detect recurring manual patterns in execution
history and propose the creation of new specialized skills.
"""

import collections
import logging
import os
import typing


class SkillProposer:
    """Analyzes execution history to suggest new specialized skills."""

    def __init__(
        self,
        ask_user_fn: typing.Callable[
            [typing.List[typing.Dict[str, typing.Any]]],
            typing.Dict[str, typing.Any]
        ],
        logger: logging.Logger
    ) -> None:
        """Initializes the proposer.
        
        Args:
            ask_user_fn: A collaborator function to prompt the user.
            logger: A logging.Logger instance for observability.
            
        Raises:
            TypeError: If ask_user_fn is not a callable or logger is not
                      a logging.Logger instance.
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
        self._proposed_cmds: typing.Set[str] = set()

    def analyze_for_new_skills(
        self,
        actual_actions: typing.List[typing.Dict[str, typing.Any]],
        repetition_threshold: int = 3
    ) -> None:
        """Analyzes actions for recurring patterns and proposes new skills.
        
        Args:
            actual_actions: Structured actions from ExecutionAnalyzer.
            repetition_threshold: The number of occurrences to trigger
                                  a proposal.
                                  
        Raises:
            TypeError: If actual_actions is not a list.
            ValueError: If repetition_threshold is not a positive integer.
        """
        if not isinstance(actual_actions, list):
            raise TypeError("actual_actions must be a list")
        if not isinstance(repetition_threshold, int) or repetition_threshold <= 0:
            raise ValueError("repetition_threshold must be a positive integer")

        self._logger.info("Analyzing for recurring patterns...")
        
        # Count shell commands
        shell_commands: typing.List[str] = [
            a.get("command", "") for a in actual_actions if a.get("type") == "shell"
        ]
        
        counts: typing.Counter[str] = collections.Counter(shell_commands)
        
        for cmd, count in counts.items():
            if count >= repetition_threshold and cmd:
                # Idempotency: Don't propose the same command twice in one session
                if cmd in self._proposed_cmds:
                    continue
                
                self._logger.info(f"Detected recurring pattern: '{cmd}' ({count} times)")
                response = self._ask_user_fn([{
                    "header": "New Skill Proposal",
                    "question": (
                        f"I detected a recurring pattern: you ran '{cmd}' "
                        f"{count} times.\nWhere would you like to save this "
                        "new specialized skill?"
                    ),
                    "type": "choice",
                    "options": [
                        {"label": "Global", "description": "Save to the central gemini-skills repository."},
                        {"label": "Local", "description": "Save to the current project's .gemini/skills/ directory."},
                        {"label": "Custom Path", "description": "Prompt for a specific directory path."},
                        {"label": "Skip", "description": "Do not create a skill at this time."}
                    ]
                }])
                
                selection = response.get("New Skill Proposal")
                
                if selection == "Custom Path":
                    path_response = self._ask_user_fn([{
                        "header": "Skill Path",
                        "question": "Please enter the absolute or relative path for the new skill:",
                        "type": "text",
                        "placeholder": "/path/to/my/skills"
                    }])
                    custom_path = path_response.get("Skill Path")
                    if custom_path:
                        os.makedirs(custom_path, exist_ok=True)
                        self._logger.info(f"Created custom skill directory: {custom_path}")
                elif selection == "Local":
                    local_path = os.path.join(".gemini", "skills")
                    os.makedirs(local_path, exist_ok=True)
                    self._logger.info(f"Ensured local skill directory: {local_path}")
                
                self._proposed_cmds.add(cmd)
