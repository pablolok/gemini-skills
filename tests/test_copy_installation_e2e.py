"""End-to-end integration tests for copy-based skill installation."""

import unittest
import os
import shutil
import tempfile
from install import SkillInstaller

class TestCopyInstallationE2E(unittest.TestCase):
    """Integration test suite for skill installation."""

    def setUp(self) -> None:
        """Set up a temporary environment for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.published_dir = os.path.join(self.test_dir, "published")
        self.project_dir = os.path.join(self.test_dir, "project")
        
        os.makedirs(self.published_dir)
        os.makedirs(self.project_dir)
        
        # Create a mock skill
        self.skill_cat = "audit"
        self.skill_name = "test-skill"
        self.skill_src_path = os.path.join(self.published_dir, self.skill_cat, self.skill_name)
        os.makedirs(self.skill_src_path)
        
        with open(os.path.join(self.skill_src_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill")
        
        with open(os.path.join(self.skill_src_path, "metadata.json"), "w") as f:
            f.write('{"name": "test-skill", "version": "1.0.0"}')
            
        self.installer = SkillInstaller(self.published_dir, lambda x: {})

    def tearDown(self) -> None:
        """Clean up the temporary environment."""
        shutil.rmtree(self.test_dir)

    def test_install_skill_copies_files(self) -> None:
        """Verify that install_skill physically copies files."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        success = self.installer.install_skill(skill_rel_path, self.project_dir)
        
        self.assertTrue(success)
        
        target_path = os.path.join(self.project_dir, ".gemini", "skills", self.skill_name)
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "metadata.json")))
        
        # Verify it's NOT a link (junction or symlink)
        self.assertFalse(os.path.islink(target_path))
        # On Windows, islink might not detect junctions from os.path, but we can check if it's a real dir
        self.assertTrue(os.path.isdir(target_path))

    def test_install_skill_overwrites_existing(self) -> None:
        """Verify that install_skill overwrites existing files."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        
        # First install
        self.installer.install_skill(skill_rel_path, self.project_dir)
        
        # Modify source
        with open(os.path.join(self.skill_src_path, "SKILL.md"), "w") as f:
            f.write("# Updated Test Skill")
            
        # Re-install
        success = self.installer.install_skill(skill_rel_path, self.project_dir)
        self.assertTrue(success)
        
        target_skill_md = os.path.join(self.project_dir, ".gemini", "skills", self.skill_name, "SKILL.md")
        with open(target_skill_md, "r") as f:
            content = f.read()
        self.assertEqual(content, "# Updated Test Skill")

if __name__ == "__main__":
    unittest.main()
