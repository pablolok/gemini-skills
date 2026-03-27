"""Tests for the SkillSelector and SkillInstaller classes."""

import os
import sys
import unittest
import io
from unittest.mock import MagicMock, patch

# We'll implement these in install.py
# For now, we'll try to import them, which will fail initially (Red phase)
from install import SkillSelector, SkillInstaller, TerminalMultiSelect, get_cli_ask_user, parse_selection_input

class TestSkillInstaller(unittest.TestCase):
    """Test suite for the SkillInstaller logic."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_ask_user = MagicMock()
        self.published_dir = "published"

    def test_installer_is_available(self) -> None:
        """Verify that the SkillInstaller class exists."""
        self.assertIsNotNone(SkillInstaller, "SkillInstaller class should be implemented in install.py")

    def test_scan_published_skills(self) -> None:
        """Verify that the installer can scan the published directory."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        skills = installer.get_available_skills()
        
        # We know we have 'audit' category with at least 4 skills from Phase 1
        self.assertIn("audit", skills)
        self.assertTrue(len(skills["audit"]) >= 4)
        self.assertIn("review-optimization", skills["audit"])

    def test_ask_user_for_skills(self) -> None:
        """Verify that the selector correctly uses ask_user."""
        if SkillSelector is None:
            self.skipTest("SkillSelector not yet implemented")

        available_skills = {
            "audit": ["skill1", "skill2"],
            "workflow": ["skill3"]
        }

        selector = SkillSelector(self.mock_ask_user)

        # Mock user selecting skill1 and skill3
        self.mock_ask_user.return_value = {
            "answers": {"0": ["audit/skill1", "workflow/skill3"]}
        }

        selected = selector.select_skills(available_skills)

        self.assertEqual(selected, ["audit/skill1", "workflow/skill3"])
        self.mock_ask_user.assert_called_once()

    def test_select_skills_formats_update_string(self) -> None:
        """Verify that updates are formatted as '[Update Available] (vX -> vY)'."""
        selector = SkillSelector(self.mock_ask_user)

        available_skills = {"category": ["skill_a"]}
        installed_skills = {"skill_a": "1.0.0"}
        updates = [{
            "name": "skill_a",
            "installed": "1.0.0",
            "latest": "2.0.0",
            "rel_path": "category/skill_a"
        }]

        # Call just to inspect the arguments passed to ask_user
        selector.select_skills(available_skills, installed_skills, updates)

        self.mock_ask_user.assert_called_once()
        args, kwargs = self.mock_ask_user.call_args

        options = args[0]["questions"][0]["options"]
        self.assertEqual(len(options), 1)
        self.assertIn("[Update Available] (1.0.0 -> 2.0.0)", options[0]["description"])
    @patch("shutil.copytree")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_copy_installation_logic(self, mock_makedirs, mock_exists, mock_copytree) -> None:
        """Verify the logic for installing skills via file copying."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        target_project = "C:/temp/project"
        skill_path = "audit/review-optimization"
        
        # .gemini/skills doesn't exist
        def exists_side_effect(path):
            if "metadata.json" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        
        installer.install_skill(skill_path, target_project)
        
        expected_target = os.path.join(target_project, ".gemini", "skills", "review-optimization")
        mock_copytree.assert_called_once_with(
            os.path.abspath(os.path.join(self.published_dir, skill_path)),
            os.path.abspath(expected_target),
            dirs_exist_ok=True
        )

    @patch("subprocess.run")
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_run_post_install_hook(self, mock_exists, mock_makedirs, mock_run) -> None:
        """Verify that the installer executes post_install.py if it exists."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        target_project = "C:/temp/project"
        skill_path = "audit/review-optimization"
        
        # Scenario: post_install.py exists, but target skill dir does not
        def side_effect(path):
            if "post_install.py" in path:
                return True
            if ".gemini" in path and "skills" in path:
                # This covers target_path check
                return False
            return True
        mock_exists.side_effect = side_effect
        
        # Mock _copy_skill_files to do nothing and isolate this test from gitignore maintenance
        with patch.object(installer, '_copy_skill_files'), patch.object(
            installer,
            'ensure_managed_gitignore_entries',
        ):
            installer.install_skill(skill_path, target_project)
            
            # Should have called subprocess.run with python and the hook path
            hook_path = os.path.abspath(os.path.join(self.published_dir, skill_path, "post_install.py"))
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertIn(sys.executable, args[0])
            self.assertIn(hook_path, args[0])

    def test_get_skill_metadata(self) -> None:
        """Verify reading metadata.json."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")

        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        # We know review-optimization has metadata.json
        metadata = installer.get_skill_metadata("audit/review-optimization")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["name"], "review-optimization")

    def test_supports_claude_reference_for_skill_name(self) -> None:
        """Verify Claude reference skills can be generated for selected skills."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        self.assertTrue(installer.supports_claude_reference("review-optimization"))
        self.assertFalse(installer.supports_claude_reference(""))

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_post_install_hook_failure(self, mock_exists, mock_run) -> None:
        """Verify handling of post-install hook failure."""
        import subprocess
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="Some error")
        
        # This should not raise, but log an error
        installer._run_post_install_hook("some/hook.py", "target/path")
        mock_run.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_manual_ask_user(self, mock_print, mock_input) -> None:
        """Verify the manual_ask_user fallback."""
        from install import manual_ask_user
        
        config = {
            "questions": [{
                "question": "Choose?",
                "options": [{"label": "opt1", "description": "desc1"}]
            }]
        }
        
        mock_input.return_value = "1"
        response = manual_ask_user(config)
        
        self.assertEqual(response["answers"]["0"], ["opt1"])
        mock_print.assert_called()

    def test_parse_selection_input_supports_multiple_styles(self) -> None:
        """Verify the lightweight prompt can parse spaces, commas, ranges, and all."""
        self.assertEqual(parse_selection_input("1 3", 4, True), [0, 2])
        self.assertEqual(parse_selection_input("1,3", 4, True), [0, 2])
        self.assertEqual(parse_selection_input("2-4", 5, True), [1, 2, 3])
        self.assertEqual(parse_selection_input("all", 3, True), [0, 1, 2])
        self.assertEqual(parse_selection_input("0", 3, False), [0])

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("builtins.print")
    def test_manual_ask_user_keyboard_interrupt(self, mock_print, mock_input) -> None:
        """Verify Ctrl+C exits the manual prompt cleanly."""
        from install import manual_ask_user

        config = {
            "questions": [{
                "question": "Choose?",
                "options": [{"label": "opt1", "description": "desc1"}]
            }]
        }

        with self.assertRaises(KeyboardInterrupt):
            manual_ask_user(config)

        mock_print.assert_called_with("\nUser closed the installer.")

    def test_terminal_multi_select_confirms_selected_items(self) -> None:
        """Verify the richer terminal selector can toggle and confirm multiple items."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "utility/skill2", "description": "desc2"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)
        keys = iter(["SPACE", "DOWN", "SPACE", "ENTER"])

        selected = selector.run(read_key=lambda: next(keys))

        self.assertEqual(selected, ["audit/skill1", "utility/skill2"])
        self.assertIn("Use arrows, space to toggle", output.getvalue())

    def test_terminal_multi_select_raises_on_quit(self) -> None:
        """Verify the richer terminal selector exits cleanly on quit."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [{"label": "audit/skill1", "description": "desc1"}],
        }
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=io.StringIO())

        with self.assertRaises(KeyboardInterrupt):
            selector.run(read_key=lambda: "q")

    @patch.dict("os.environ", {}, clear=True)
    @patch("sys.stdin.isatty", return_value=True)
    @patch("sys.stdout.isatty", return_value=True)
    def test_get_cli_ask_user_prefers_terminal_selector(self, _mock_stdout, _mock_stdin) -> None:
        """Verify the CLI uses the richer selector in a real terminal."""
        from install import terminal_ask_user

        ask_user = get_cli_ask_user([])

        self.assertIs(ask_user, terminal_ask_user)

    @patch.dict("os.environ", {}, clear=True)
    @patch("sys.stdin.isatty", return_value=True)
    @patch("sys.stdout.isatty", return_value=True)
    def test_get_cli_ask_user_supports_simple_flag(self, _mock_stdout, _mock_stdin) -> None:
        """Verify the simple flag keeps the lightweight prompt."""
        from install import manual_ask_user

        ask_user = get_cli_ask_user(["--simple"])

        self.assertIs(ask_user, manual_ask_user)

    @patch("install.SkillInstaller")
    @patch("install.SkillSelector")
    @patch("install.get_cli_ask_user")
    @patch("os.path.exists")
    def test_main_function(self, mock_exists, mock_get_cli_ask_user, mock_selector, mock_installer) -> None:
        """Verify that main runs the installation flow."""
        from install import main
        
        mock_exists.return_value = True
        mock_get_cli_ask_user.return_value = MagicMock(return_value={"answers": {"0": "no"}})
        
        # Mock available skills
        mock_inst_instance = mock_installer.return_value
        mock_inst_instance.get_available_skills.return_value = {"audit": ["skill1"]}
        mock_inst_instance.supports_codex_bridge.return_value = False
        mock_inst_instance.supports_claude_reference.return_value = False
        
        # Mock skill selection
        mock_sel_instance = mock_selector.return_value
        mock_sel_instance.select_skills.return_value = ["audit/skill1"]
        
        main()
        
        mock_inst_instance.get_available_skills.assert_called_once()
        mock_sel_instance.select_skills.assert_called_once()
        mock_inst_instance.install_skill.assert_called_once_with("audit/skill1", os.getcwd())
        mock_inst_instance.ensure_managed_gitignore_entries.assert_called_with(os.getcwd())

    @patch("install.SkillInstaller")
    @patch("install.SkillSelector")
    @patch("install.get_cli_ask_user")
    @patch("os.path.exists")
    def test_main_function_refreshes_gitignore_even_when_nothing_is_selected(
        self,
        mock_exists,
        mock_get_cli_ask_user,
        mock_selector,
        mock_installer,
    ) -> None:
        """Verify the managed gitignore block is refreshed even on an empty selection."""
        from install import main

        mock_exists.return_value = True
        mock_get_cli_ask_user.return_value = MagicMock(return_value={"answers": {"0": "no"}})

        mock_inst_instance = mock_installer.return_value
        mock_inst_instance.get_available_skills.return_value = {"audit": ["skill1"]}
        mock_inst_instance.supports_codex_bridge.return_value = False
        mock_inst_instance.supports_claude_reference.return_value = False

        mock_sel_instance = mock_selector.return_value
        mock_sel_instance.select_skills.return_value = []

        main()

        mock_inst_instance.install_skill.assert_not_called()
        mock_inst_instance.ensure_managed_gitignore_entries.assert_called_with(os.getcwd())

    @patch("sys.exit")
    @patch("os.path.exists")
    def test_main_function_missing_dir(self, mock_exists, mock_exit) -> None:
        """Verify that main exits if published dir is missing."""
        from install import main
        mock_exists.return_value = False
        
        main()
        mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
