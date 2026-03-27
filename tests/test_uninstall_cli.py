"""Tests for the uninstall CLI entry point."""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

import uninstall


class TestUninstallCli(unittest.TestCase):
    @patch("uninstall.RUNTIME")
    @patch("uninstall.SkillSelector")
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
            mock_runtime.uninstall_named_skills.return_value = ["review-optimization"]

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills.return_value = ["managed/review-optimization"]

            uninstall.main()

            mock_sel_instance.select_skills.assert_called_once()
            mock_runtime.uninstall_named_skills.assert_called_once_with(
                ["review-optimization"],
                temp_dir,
            )
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

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills.return_value = []

            uninstall.main()

            mock_runtime.uninstall_named_skills.assert_not_called()
            mock_print.assert_any_call("No skills selected.")
