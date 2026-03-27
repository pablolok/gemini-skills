"""Tests for the skill-manager launcher wrapper."""

import unittest
from unittest.mock import MagicMock, patch

import manage


class TestManageCli(unittest.TestCase):
    @patch("install.main")
    @patch("manage.get_cli_ask_user")
    def test_main_launches_installer(self, mock_get_cli_ask_user, mock_install_main) -> None:
        ask_user = MagicMock(return_value={"answers": {"0": "install"}})
        mock_get_cli_ask_user.return_value = ask_user

        manage.main()

        ask_user.assert_called_once()
        mock_install_main.assert_called_once()

    @patch("uninstall.main")
    @patch("manage.get_cli_ask_user")
    def test_main_launches_uninstaller(self, mock_get_cli_ask_user, mock_uninstall_main) -> None:
        ask_user = MagicMock(return_value={"answers": {"0": "uninstall"}})
        mock_get_cli_ask_user.return_value = ask_user

        manage.main()

        ask_user.assert_called_once()
        mock_uninstall_main.assert_called_once()

    @patch("builtins.print")
    @patch("manage.get_cli_ask_user")
    def test_main_reports_empty_selection(self, mock_get_cli_ask_user, mock_print) -> None:
        ask_user = MagicMock(return_value={"answers": {"0": ""}})
        mock_get_cli_ask_user.return_value = ask_user

        manage.main()

        mock_print.assert_called_once_with("No skill-manager flow selected.")
