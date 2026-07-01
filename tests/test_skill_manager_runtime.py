"""Tests for the installed skill-manager runtime helpers."""

import importlib.util
import os
import tempfile
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
    def test_resolve_published_dir_falls_back_to_bundled_repo_checkout(self) -> None:
        """Verify source-repo runtime works without an installed runtime_config.json."""
        with tempfile.TemporaryDirectory() as temp_dir:
            published_dir = RUNTIME.resolve_published_dir(root=temp_dir)

        expected = os.path.abspath("published")
        self.assertEqual(published_dir, expected)

    def test_install_named_skills_installs_as_claude_skill(self) -> None:
        """Verify runtime installs each named skill as a real Claude skill."""
        installer = MagicMock()
        installer.install_skill.return_value = True

        with patch.object(RUNTIME, "build_installer", return_value=installer), patch.object(
            RUNTIME,
            "list_available_skill_paths",
            return_value=["utility/subagent-balancer"],
        ):
            installed = RUNTIME.install_named_skills(
                ["utility/subagent-balancer"],
                root=os.getcwd(),
            )

        self.assertEqual(installed, ["utility/subagent-balancer"])
        installer.install_skill.assert_called_once_with(
            "utility/subagent-balancer", os.getcwd()
        )

    def test_uninstall_named_skills_uses_installer_uninstall(self) -> None:
        """Verify runtime uninstall delegates to the installer cleanup flow."""
        installer = MagicMock()
        installer.uninstall_skill.return_value = True

        with patch.object(RUNTIME, "build_installer", return_value=installer):
            removed = RUNTIME.uninstall_named_skills(["review-optimization"], root=os.getcwd())

        self.assertEqual(removed, ["review-optimization"])
        installer.uninstall_skill.assert_called_once_with("review-optimization", os.getcwd())

    def test_uninstall_named_skills_continues_after_os_error(self) -> None:
        """Verify runtime uninstall continues when one skill removal fails."""
        installer = MagicMock()
        installer.uninstall_skill.side_effect = [PermissionError("locked"), True]

        with patch.object(RUNTIME, "build_installer", return_value=installer):
            removed = RUNTIME.uninstall_named_skills(
                ["compliance-audit-c#", "review-optimization"],
                root=os.getcwd(),
            )

        self.assertEqual(removed, ["review-optimization"])

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
