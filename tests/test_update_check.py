"""Tests for the update check logic."""

import unittest
import os
import shutil
import tempfile
import json
from install import SkillInstaller

class TestUpdateCheck(unittest.TestCase):
    """Test suite for skill update detection."""

    def setUp(self) -> None:
        """Set up a temporary environment for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.published_dir = os.path.join(self.test_dir, "published")
        self.project_dir = os.path.join(self.test_dir, "project")
        
        os.makedirs(self.published_dir)
        os.makedirs(self.project_dir)
        
        # Create a mock skill category
        self.skill_cat = "audit"
        self.skill_name = "test-skill"
        self.skill_src_path = os.path.join(self.published_dir, self.skill_cat, self.skill_name)
        os.makedirs(self.skill_src_path)
        
        # Latest version in published
        with open(os.path.join(self.skill_src_path, "metadata.json"), "w") as f:
            json.dump({"name": "test-skill", "version": "1.1.0"}, f)
            
        # Target project with older version installed
        self.target_skill_path = os.path.join(self.project_dir, ".gemini", "skills", self.skill_name)
        os.makedirs(self.target_skill_path)
        with open(os.path.join(self.target_skill_path, "metadata.json"), "w") as f:
            json.dump({"name": "test-skill", "version": "1.0.0"}, f)
            
        self.installer = SkillInstaller(self.published_dir, lambda x: {})

    def tearDown(self) -> None:
        """Clean up the temporary environment."""
        shutil.rmtree(self.test_dir)

    def test_check_for_updates_finds_newer(self) -> None:
        """Verify that a newer version is correctly detected."""
        updates = self.installer.check_for_updates(self.project_dir)
        
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]["name"], "test-skill")
        self.assertEqual(updates[0]["installed"], "1.0.0")
        self.assertEqual(updates[0]["latest"], "1.1.0")

    def test_check_for_updates_no_newer(self) -> None:
        """Verify that same or older versions are ignored."""
        # Update project to match published
        with open(os.path.join(self.target_skill_path, "metadata.json"), "w") as f:
            json.dump({"name": "test-skill", "version": "1.1.0"}, f)
            
        updates = self.installer.check_for_updates(self.project_dir)
        self.assertEqual(len(updates), 0)

    def test_check_for_updates_missing_metadata(self) -> None:
        """Verify handling of missing metadata in project or published."""
        # Remove metadata from project
        os.remove(os.path.join(self.target_skill_path, "metadata.json"))
        
        updates = self.installer.check_for_updates(self.project_dir)
        self.assertEqual(len(updates), 0)

if __name__ == "__main__":
    unittest.main()
