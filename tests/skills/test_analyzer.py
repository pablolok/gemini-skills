"""Test suite for the execution log analyzer."""

import os
import typing
import unittest

import importlib
analyzer = importlib.import_module("skills.review-optimization.analyzer")


class TestExecutionAnalyzer(unittest.TestCase):
    """Test suite for verifying the logic of the execution log analyzer."""

    def test_parse_tool_calls(self) -> None:
        """Verify that the analyzer can parse various tool calls."""
        exec_analyzer: analyzer.ExecutionAnalyzer = analyzer.ExecutionAnalyzer()
        history: typing.List[typing.Dict[str, typing.Any]] = [
            {"tool": "read_file", "args": {"file_path": "plan.md"}},
            {"tool": "list_directory", "args": {"dir_path": "src"}},
            {"tool": "glob", "args": {"pattern": "*.py"}},
            {"tool": "grep_search", "args": {"pattern": "TODO"}},
            {"tool": "replace", "args": {"file_path": "app.py"}},
            {"tool": "write_file", "args": {"file_path": "new.py"}},
            {"tool": "run_shell_command", "args": {"command": "npm test"}},
            {"tool": "activate_skill", "args": {"name": "test-skill"}},
            {"tool": "unknown_tool", "args": {}},
            {"tool": "tool_with_none_args", "args": None}
        ]
        actions: typing.List[typing.Dict[str, typing.Any]] = (
            exec_analyzer.parse_history(history)
        )
        self.assertEqual(len(actions), 10)
        self.assertEqual(actions[0]["type"], "read")
        self.assertEqual(actions[4]["type"], "edit")
        self.assertEqual(actions[6]["type"], "shell")
        self.assertEqual(actions[7]["type"], "skill")
        self.assertEqual(actions[8]["type"], "other")
        self.assertEqual(actions[9]["type"], "other")

    def test_parse_history_invalid_input(self) -> None:
        """Verify that parse_history raises TypeError for invalid input."""
        exec_analyzer: analyzer.ExecutionAnalyzer = analyzer.ExecutionAnalyzer()
        with self.assertRaises(TypeError):
            exec_analyzer.parse_history("not a list")  # type: ignore


class TestPathFormatter(unittest.TestCase):
    """Test suite for verifying the logic of the implementation path formatter."""

    def test_format_path(self) -> None:
        """Verify that the formatter can create human-readable paths."""
        formatter: analyzer.PathFormatter = analyzer.PathFormatter()
        actions: typing.List[typing.Dict[str, typing.Any]] = [
            {"type": "read", "target": "plan.md"},
            {"type": "shell", "command": "npm test"},
            {"type": "edit", "target": os.path.join("src", "app.js")},
            {"type": "skill", "name": "my-skill"},
            {"type": "other", "tool": "mystery"}
        ]
        path: typing.List[str] = formatter.format_path(actions)
        self.assertEqual(len(path), 5)
        self.assertIn("Read plan.md", path[0])
        self.assertIn("Run npm test", path[1])
        self.assertIn(f"Edit {os.path.join('src', 'app.js')}", path[2])
        self.assertIn("Activate skill my-skill", path[3])
        self.assertIn("Used tool mystery", path[4])

    def test_format_path_invalid_input(self) -> None:
        """Verify that format_path raises TypeError for invalid input."""
        formatter: analyzer.PathFormatter = analyzer.PathFormatter()
        with self.assertRaises(TypeError):
            formatter.format_path(None)  # type: ignore


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
