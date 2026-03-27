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

    def test_uninstall_named_skills_uses_installer_uninstall(self) -> None:
        """Verify runtime uninstall delegates to the installer cleanup flow."""
        installer = MagicMock()
        installer.uninstall_skill.return_value = True

        with patch.object(RUNTIME, "build_installer", return_value=installer):
            removed = RUNTIME.uninstall_named_skills(["review-optimization"], root=os.getcwd())

        self.assertEqual(removed, ["review-optimization"])
        installer.uninstall_skill.assert_called_once_with("review-optimization", os.getcwd())

    def test_list_managed_installed_skills_filters_unmanaged_entries(self) -> None:
        """Verify runtime exposes only managed installed skills for uninstall flows."""
        installer = MagicMock()
        installer.get_managed_skill_names.return_value = ["review-optimization"]

        with patch.object(RUNTIME, "build_installer", return_value=installer), patch.object(
            RUNTIME,
            "list_installed_skills",
            return_value=[
                {"name": "review-optimization", "version": "1.0.0"},
                {"name": "changelog-manager", "version": "1.0.0"},
            ],
        ):
            listed = RUNTIME.list_managed_installed_skills(root=os.getcwd())

        self.assertEqual(listed, [{"name": "review-optimization", "version": "1.0.0"}])
