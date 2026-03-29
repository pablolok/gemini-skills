"""Tests for the uninstall CLI entry point."""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

import uninstall


class TestUninstallCli(unittest.TestCase):
    @patch("uninstall.RUNTIME")
    @patch("uninstall.SkillSelector")
    @patch("manage.main")
    @patch("uninstall.get_cli_ask_user")
    @patch("uninstall.logging.getLogger")
    @patch("builtins.print")
    @patch("os.getcwd")
    def test_main_runs_uninstall_flow(
        self,
        mock_getcwd,
        mock_print,
        mock_get_logger,
        mock_get_cli_ask_user,
        mock_manage_main,
        mock_selector,
        mock_runtime,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock()
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_runtime.list_managed_installed_skills.return_value = [
                {"name": "review-optimization", "version": "1.0.0"},
            ]
            mock_runtime.list_available_skill_paths.return_value = [
                "audit/review-optimization",
            ]
            mock_runtime.uninstall_named_skills.return_value = ["review-optimization"]

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills_with_action.return_value = (["audit/review-optimization"], None)

            uninstall.main()

            mock_sel_instance.select_skills_with_action.assert_called_once()
            _args, kwargs = mock_sel_instance.select_skills_with_action.call_args
            self.assertEqual(kwargs["question_text"], "Which managed skills would you like to uninstall?")
            self.assertEqual(kwargs["banner_subtitle"], "Skill-Manager Uninstaller")
            mock_runtime.uninstall_named_skills.assert_called_once_with(
                ["review-optimization"],
                temp_dir,
            )
            mock_manage_main.assert_not_called()
            mock_print.assert_any_call(f"Target project: {temp_dir}")
            mock_print.assert_any_call("Removed 1 managed skill(s):")
            mock_print.assert_any_call("- review-optimization")

    @patch("uninstall.RUNTIME")
    @patch("uninstall.get_cli_ask_user")
    @patch("uninstall.logging.getLogger")
    @patch("builtins.print")
    @patch("os.getcwd")
    def test_main_reports_no_managed_skills(
        self,
        mock_getcwd,
        mock_print,
        mock_get_logger,
        mock_get_cli_ask_user,
        mock_runtime,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock()
            mock_get_logger.return_value = MagicMock()
            mock_runtime.list_managed_installed_skills.return_value = []
            mock_runtime.list_available_skill_paths.return_value = []

            uninstall.main()

            mock_runtime.uninstall_named_skills.assert_not_called()
            mock_print.assert_any_call("No managed skills found to uninstall.")

    @patch("uninstall.RUNTIME")
    @patch("uninstall.SkillSelector")
    @patch("uninstall.get_cli_ask_user")
    @patch("uninstall.logging.getLogger")
    @patch("builtins.print")
    @patch("os.getcwd")
    def test_main_reports_no_selection(
        self,
        mock_getcwd,
        mock_print,
        mock_get_logger,
        mock_get_cli_ask_user,
        mock_selector,
        mock_runtime,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock()
            mock_get_logger.return_value = MagicMock()
            mock_runtime.list_managed_installed_skills.return_value = [
                {"name": "review-optimization", "version": "1.0.0"},
            ]
            mock_runtime.list_available_skill_paths.return_value = [
                "audit/review-optimization",
            ]

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills_with_action.return_value = ([], None)

            uninstall.main()

            mock_runtime.uninstall_named_skills.assert_not_called()
            mock_print.assert_any_call("No skills selected.")

    @patch("uninstall.RUNTIME")
    @patch("uninstall.SkillSelector")
    @patch("manage.main")
    @patch("uninstall.get_cli_ask_user")
    @patch("uninstall.logging.getLogger")
    @patch("os.getcwd")
    def test_main_returns_to_manager_on_back_action(
        self,
        mock_getcwd,
        mock_get_logger,
        mock_get_cli_ask_user,
        mock_manage_main,
        mock_selector,
        mock_runtime,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock()
            mock_get_logger.return_value = MagicMock()
            mock_runtime.list_managed_installed_skills.return_value = [
                {"name": "review-optimization", "version": "1.0.0"},
            ]
            mock_runtime.list_available_skill_paths.return_value = [
                "audit/review-optimization",
            ]

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills_with_action.return_value = ([], "back_to_manager")

            uninstall.main()

            mock_manage_main.assert_called_once()
            mock_runtime.uninstall_named_skills.assert_not_called()

    def test_build_uninstall_options_groups_by_catalog_category(self) -> None:
        options = uninstall.build_uninstall_options(
            [
                {"name": "review-optimization", "version": "1.0.0"},
                {"name": "skill-manager", "version": "1.0.0"},
                {"name": "local-only", "version": "1.0.0"},
            ],
            [
                "audit/review-optimization",
                "utility/skill-manager",
            ],
        )

        self.assertEqual(
            options,
            {
                "audit": ["review-optimization"],
                "managed": ["local-only"],
                "utility": ["skill-manager"],
            },
        )
