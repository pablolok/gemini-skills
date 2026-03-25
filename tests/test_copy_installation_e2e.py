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
        self.codex_source_dir = os.path.join(self.test_dir, ".codex", "skills")
        
        os.makedirs(self.published_dir)
        os.makedirs(self.project_dir)
        os.makedirs(self.codex_source_dir)
        
        # Create a mock skill
        self.skill_cat = "audit"
        self.skill_name = "test-skill"
        self.skill_src_path = os.path.join(self.published_dir, self.skill_cat, self.skill_name)
        os.makedirs(self.skill_src_path)
        
        with open(os.path.join(self.skill_src_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill")
        
        with open(os.path.join(self.skill_src_path, "metadata.json"), "w") as f:
            f.write('{"name": "test-skill", "version": "1.0.0"}')
        
        with open(os.path.join(self.skill_src_path, "CHANGELOG.md"), "w") as f:
            f.write("# Changelog\n\n- Initial version")

        self.codex_bridge_path = os.path.join(self.codex_source_dir, self.skill_name)
        os.makedirs(self.codex_bridge_path)
        with open(os.path.join(self.codex_bridge_path, "SKILL.md"), "w") as f:
            f.write("# Test Codex Bridge")
            
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
        self.assertTrue(os.path.isfile(os.path.join(target_path, "CHANGELOG.md")))
        
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

    def test_install_codex_bridge_copies_wrapper(self) -> None:
        """Verify that install_codex_bridge copies the lightweight wrapper."""
        success = self.installer.install_codex_bridge(self.skill_name, self.project_dir)

        self.assertTrue(success)

        target_path = os.path.join(self.project_dir, ".codex", "skills", self.skill_name)
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "SKILL.md")))

        with open(os.path.join(target_path, "SKILL.md"), "r") as f:
            content = f.read()
        self.assertEqual(content, "# Test Codex Bridge")

    @unittest.skipUnless(os.name == "nt", "Windows junction tests only run on Windows")
    def test_transition_from_junction_to_copy(self) -> None:
        """Verify that a legacy junction is correctly replaced by a copy."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        target_skills_dir = os.path.join(self.project_dir, ".gemini", "skills")
        os.makedirs(target_skills_dir, exist_ok=True)
        target_path = os.path.join(target_skills_dir, self.skill_name)
        
        # Create a real junction manually
        import subprocess
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/J", target_path, os.path.abspath(self.skill_src_path)],
            check=True, capture_output=True, text=True
        )
        print(f"\nmklink output: {res.stdout}")
        
        # Verify it IS a link
        is_link = os.path.islink(target_path)
        print(f"Is link? {is_link}")
        
        # Check attributes
        import ctypes
        attrs = ctypes.windll.kernel32.GetFileAttributesW(target_path)
        print(f"Attributes: {attrs}")
        # FILE_ATTRIBUTE_REPARSE_POINT = 0x400
        print(f"Is reparse point? {bool(attrs & 0x400)}")
        
        self.assertTrue(is_link or bool(attrs & 0x400))
        
        # Install via our tool
        success = self.installer.install_skill(skill_rel_path, self.project_dir)
        self.assertTrue(success)
        
        # Verify it IS NO LONGER a link
        self.assertFalse(os.path.islink(target_path))
        self.assertTrue(os.path.isdir(target_path))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "SKILL.md")))

if __name__ == "__main__":
    unittest.main()
