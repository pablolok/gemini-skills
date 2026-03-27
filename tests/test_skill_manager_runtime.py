"""Tests for the installed skill-manager runtime helpers."""

import importlib.util
import os
import unittest
from unittest.mock import MagicMock, patch


def _load_module(module_name: str, path: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RUNTIME = _load_module(
    "skill_manager_runtime",
    os.path.join("skills", "skill-manager", "scripts", "runtime.py"),
)


class TestSkillManagerRuntime(unittest.TestCase):
    def test_install_named_skills_respects_companion_support_flags(self) -> None:
        """Verify runtime installs skip Codex and Claude companions for Gemini-only skills."""
        installer = MagicMock()
        installer.install_skill.return_value = True
        installer.supports_codex_bridge.return_value = False
        installer.supports_claude_reference.return_value = False

        with patch.object(RUNTIME, "build_installer", return_value=installer), patch.object(
            RUNTIME,
            "list_available_skill_paths",
            return_value=["utility/subagent-balancer"],
        ):
            installed = RUNTIME.install_named_skills(
                ["utility/subagent-balancer"],
                root=os.getcwd(),
                include_codex_bridges=True,
                include_claude_references=True,
            )

        self.assertEqual(installed, ["utility/subagent-balancer"])
        installer.install_codex_bridge.assert_not_called()
        installer.install_claude_reference.assert_not_called()
