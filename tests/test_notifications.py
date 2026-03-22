"""Tests for update notifications."""

import unittest
from unittest.mock import MagicMock
from install import SkillInstaller

class TestNotifications(unittest.TestCase):
    """Test suite for update notification formatting."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.installer = SkillInstaller("published", lambda x: {}, logger=self.logger)

    def test_notify_updates_with_content(self) -> None:
        """Verify that notifications are correctly logged."""
        updates = [
            {"name": "skill1", "installed": "1.0.0", "latest": "1.1.0"},
            {"name": "skill2", "installed": "2.0.0", "latest": "3.0.0"}
        ]
        
        self.installer.notify_updates(updates)
        
        # Check if logger.info was called with relevant info
        self.assertTrue(any("skill1" in str(call) for call in self.logger.info.call_args_list))
        self.assertTrue(any("1.1.0" in str(call) for call in self.logger.info.call_args_list))
        self.assertTrue(any("skill2" in str(call) for call in self.logger.info.call_args_list))
        self.assertTrue(any("3.0.0" in str(call) for call in self.logger.info.call_args_list))

    def test_notify_updates_empty(self) -> None:
        """Verify that no notification is logged if there are no updates."""
        self.installer.notify_updates([])
        self.logger.info.assert_not_called()

if __name__ == "__main__":
    unittest.main()
