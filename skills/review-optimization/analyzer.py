"""Execution log analyzer for reconstructing the implementation path.

This module provides classes for parsing tool call history and formatting
the implementation path into a human-readable format.

Classes:
    ExecutionAnalyzer: Parses raw tool calls into structured actions.
    PathFormatter: Formats structured actions into human-readable strings.
"""

import logging
import typing


class ExecutionAnalyzer:
    """Analyzes session history to identify tool call sequences."""

    def __init__(self, logger: typing.Optional[logging.Logger] = None) -> None:
        """Initializes the analyzer with an optional logger.
        
        Args:
            logger: A logging.Logger instance for observability.
        """
        self._logger: logging.Logger = logger or logging.getLogger(__name__)

    def parse_history(
        self, history: typing.List[typing.Dict[str, typing.Any]]
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Parses a list of tool call objects into structured actions.
        
        Args:
            history: A list of dicts, each representing a tool call.
            
        Returns:
            A list of dicts, each representing a structured action.
            
        Raises:
            TypeError: If history is not a list.
        """
        if not isinstance(history, list):
            self._logger.error(f"Input 'history' must be a list, got {type(history)}")
            raise TypeError("history must be a list")

        self._logger.info(f"Parsing history with {len(history)} tool calls")
        actions: typing.List[typing.Dict[str, typing.Any]] = []
        for call in history:
            tool: str = call.get("tool", "")
            # Ensure args is a dict even if it's explicitly None in the call
            args: typing.Dict[str, typing.Any] = call.get("args") or {}
            
            if tool in ["read_file", "list_directory", "glob", "grep_search"]:
                target: str = (
                    args.get("file_path") or
                    args.get("dir_path") or
                    args.get("pattern") or
                    "unknown"
                )
                actions.append({
                    "type": "read",
                    "tool": tool,
                    "target": target
                })
            elif tool in ["replace", "write_file"]:
                actions.append({
                    "type": "edit",
                    "tool": tool,
                    "target": args.get("file_path")
                })
            elif tool == "run_shell_command":
                actions.append({
                    "type": "shell",
                    "command": args.get("command")
                })
            elif tool == "activate_skill":
                actions.append({
                    "type": "skill",
                    "name": args.get("name")
                })
            else:
                actions.append({
                    "type": "other",
                    "tool": tool
                })
        return actions


class PathFormatter:
    """Formats structured actions into human-readable implementation paths."""

    def __init__(self, logger: typing.Optional[logging.Logger] = None) -> None:
        """Initializes the formatter with an optional logger.
        
        Args:
            logger: A logging.Logger instance for observability.
        """
        self._logger: logging.Logger = logger or logging.getLogger(__name__)

    def format_path(
        self, actions: typing.List[typing.Dict[str, typing.Any]]
    ) -> typing.List[str]:
        """Reconstructs a human-readable implementation path from actions.
        
        Args:
            actions: A list of structured actions.
            
        Returns:
            A list of strings describing the path.
            
        Raises:
            TypeError: If actions is not a list.
        """
        if not isinstance(actions, list):
            self._logger.error(f"Input 'actions' must be a list, got {type(actions)}")
            raise TypeError("actions must be a list")

        self._logger.info(f"Formatting path from {len(actions)} actions")
        path: typing.List[str] = []
        for action in actions:
            action_type: str = action.get("type", "other")
            if action_type == "read":
                path.append(f"Read {action.get('target')}")
            elif action_type == "edit":
                path.append(f"Edit {action.get('target')}")
            elif action_type == "shell":
                path.append(f"Run {action.get('command')}")
            elif action_type == "skill":
                path.append(f"Activate skill {action.get('name')}")
            else:
                path.append(f"Used tool {action.get('tool')}")
        return path
