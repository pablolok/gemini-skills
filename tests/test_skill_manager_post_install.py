"""Tests for skill-manager Gemini integration setup."""

import io
import importlib.util
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


def _load_module(module_name: str, path: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


POST_INSTALL = _load_module(
    "skill_manager_post_install",
    os.path.join("skills", "skill-manager", "post_install.py"),
)
SESSION_START_HOOK = _load_module(
    "skill_manager_session_start_hook",
    os.path.join("skills", "skill-manager", "scripts", "session_start_hook.py"),
)


class TestSkillManagerPostInstall(unittest.TestCase):
    def test_integrate_writes_settings_command_and_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    "GEMINI_SKILLS_REPO_ROOT": os.path.abspath("."),
                    "GEMINI_SKILLS_PUBLISHED_DIR": os.path.abspath("published"),
                },
                clear=False,
            ):
                POST_INSTALL.integrate(temp_dir)

            settings_path = os.path.join(temp_dir, ".gemini", "settings.json")
            command_dir = os.path.join(temp_dir, ".gemini", "commands", "skill-manager")
            config_path = os.path.join(temp_dir, ".gemini", "skills", "skill-manager", "runtime_config.json")

            self.assertTrue(os.path.exists(settings_path))
            self.assertTrue(os.path.exists(os.path.join(command_dir, "list.toml")))
            self.assertTrue(os.path.exists(os.path.join(command_dir, "install.toml")))
            self.assertTrue(os.path.exists(os.path.join(command_dir, "update.toml")))
            self.assertTrue(os.path.exists(os.path.join(command_dir, "uninstall.toml")))
            self.assertTrue(os.path.exists(config_path))

            with open(settings_path, "r", encoding="utf-8") as handle:
                settings = json.load(handle)

            hooks = settings["hooks"]["SessionStart"]
            self.assertEqual(len(hooks), 1)
            self.assertEqual(hooks[0]["matcher"], "startup")
            self.assertEqual(hooks[0]["hooks"][0]["name"], POST_INSTALL.HOOK_NAME)
            self.assertIn("run_shell_command(python)", settings["tools"]["core"])

            with open(os.path.join(command_dir, "update.toml"), "r", encoding="utf-8") as handle:
                update_command = handle.read()
            with open(os.path.join(command_dir, "list.toml"), "r", encoding="utf-8") as handle:
                list_command = handle.read()

            self.assertIn("Update installed Gemini skills", update_command)
            self.assertIn("python .gemini/skills/skill-manager/scripts/update_skills.py", update_command)
            self.assertIn("python .gemini/skills/skill-manager/scripts/list_skills.py", list_command)

            with open(config_path, "r", encoding="utf-8") as handle:
                config = json.load(handle)

            self.assertTrue(config["source_repo_root"].endswith("gemini-skills"))
            self.assertTrue(config["published_dir"].endswith(os.path.join("gemini-skills", "published")))

    def test_integrate_is_idempotent_for_session_start_hook(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    "GEMINI_SKILLS_REPO_ROOT": os.path.abspath("."),
                    "GEMINI_SKILLS_PUBLISHED_DIR": os.path.abspath("published"),
                },
                clear=False,
            ):
                POST_INSTALL.integrate(temp_dir)
                POST_INSTALL.integrate(temp_dir)

            settings_path = os.path.join(temp_dir, ".gemini", "settings.json")
            with open(settings_path, "r", encoding="utf-8") as handle:
                settings = json.load(handle)

            hooks = settings["hooks"]["SessionStart"]
            self.assertEqual(len(hooks), 1)
            self.assertEqual(len(hooks[0]["hooks"]), 1)
            self.assertEqual(settings["tools"]["core"].count("run_shell_command(python)"), 1)

    def test_integrate_preserves_existing_broad_shell_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, ".gemini", "settings.json")
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as handle:
                json.dump({"tools": {"core": ["run_shell_command"]}}, handle)

            with patch.dict(
                os.environ,
                {
                    "GEMINI_SKILLS_REPO_ROOT": os.path.abspath("."),
                    "GEMINI_SKILLS_PUBLISHED_DIR": os.path.abspath("published"),
                },
                clear=False,
            ):
                POST_INSTALL.integrate(temp_dir)

            with open(settings_path, "r", encoding="utf-8") as handle:
                settings = json.load(handle)

            self.assertIn("run_shell_command", settings["tools"]["core"])
            self.assertNotIn("run_shell_command(python)", settings["tools"]["core"])


class TestSkillManagerSessionStartHook(unittest.TestCase):
    @patch.object(SESSION_START_HOOK, "check_updates", return_value=[])
    def test_session_start_hook_returns_empty_json_when_no_updates(self, _mock_updates) -> None:
        with patch("sys.stdin", io.StringIO("{}")), io.StringIO() as stdout, redirect_stdout(stdout):
            SESSION_START_HOOK.main()
            self.assertEqual(stdout.getvalue().strip(), "{}")

    @patch.object(
        SESSION_START_HOOK,
        "check_updates",
        return_value=[{"name": "subagent-balancer", "installed": "1.6.0", "latest": "1.6.1"}],
    )
    def test_session_start_hook_reports_updates(self, _mock_updates) -> None:
        with patch("sys.stdin", io.StringIO("{}")), io.StringIO() as stdout, redirect_stdout(stdout):
            SESSION_START_HOOK.main()
            payload = json.loads(stdout.getvalue())
            self.assertIn("/skill-manager:update", payload["systemMessage"])
            self.assertIn("subagent-balancer", payload["systemMessage"])
