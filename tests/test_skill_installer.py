"""Tests for the SkillSelector and SkillInstaller classes."""

import os
import unittest
from unittest.mock import MagicMock, patch
import json

# We'll implement these in install.py
# For now, we'll try to import them, which will fail initially (Red phase)
from install import SkillSelector, SkillInstaller

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
            "Select Skills": ["audit/skill1", "workflow/skill3"]
        }
        
        selected = selector.select_skills(available_skills)
        
        self.assertEqual(selected, ["audit/skill1", "workflow/skill3"])
        self.mock_ask_user.assert_called_once()

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_junction_logic(self, mock_makedirs, mock_exists) -> None:
        """Verify the logic for creating directory junctions."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        target_project = "C:/temp/project"
        skill_path = "audit/review-optimization"
        
        mock_exists.return_value = False # .gemini/skills doesn't exist
        
        # We'll mock the actual junction command in the implementation
        with patch.object(installer, '_create_junction') as mock_junction:
            installer.install_skill(skill_path, target_project)
            
            expected_target = os.path.join(target_project, ".gemini", "skills", "review-optimization")
            mock_junction.assert_called_once_with(
                os.path.abspath(os.path.join(self.published_dir, skill_path)),
                os.path.abspath(expected_target)
            )

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_run_post_install_hook(self, mock_exists, mock_run) -> None:
        """Verify that the installer executes post_install.py if it exists."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        target_project = "C:/temp/project"
        skill_path = "audit/review-optimization"
        
        # Scenario: post_install.py exists
        def side_effect(path):
            if "post_install.py" in path:
                return True
            return True
        mock_exists.side_effect = side_effect
        
        # Mock _create_junction to do nothing
        with patch.object(installer, '_create_junction'):
            installer.install_skill(skill_path, target_project)
            
            # Should have called subprocess.run with python and the hook path
            hook_path = os.path.abspath(os.path.join(self.published_dir, skill_path, "post_install.py"))
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertIn(sys.executable, args[0])
            self.assertIn(hook_path, args[0])

if __name__ == "__main__":
    unittest.main()
