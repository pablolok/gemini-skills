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
            f.write(
                "---\n"
                "name: test-skill\n"
                "description: Test Codex bridge.\n"
                "---\n\n"
                "# Test Codex Bridge\n"
            )
            
        self.installer = SkillInstaller(self.published_dir, lambda x: {})

    def tearDown(self) -> None:
        """Clean up the temporary environment."""
        shutil.rmtree(self.test_dir)

    def test_install_skill_copies_files(self) -> None:
        """Verify that install_skill physically copies files."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        success = self.installer.install_skill(skill_rel_path, self.project_dir)
        
        self.assertTrue(success)
        
        # test-skill is not in install.config.json so it defaults to shared → .agents/skills/
        target_path = os.path.join(self.project_dir, ".agents", "skills", self.skill_name)
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "metadata.json")))
        self.assertTrue(os.path.isfile(os.path.join(target_path, "CHANGELOG.md")))
        with open(os.path.join(self.project_dir, ".gitignore"), "r", encoding="utf-8") as f:
            gitignore = f.read()
        self.assertIn(f".agents/skills/{self.skill_name}/", gitignore)
        self.assertNotIn(".agents/skills/\n", gitignore)
        
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
        
        # test-skill defaults to shared → .agents/skills/
        target_skill_md = os.path.join(self.project_dir, ".agents", "skills", self.skill_name, "SKILL.md")
        with open(target_skill_md, "r") as f:
            content = f.read()
        self.assertEqual(content, "# Updated Test Skill")

    def test_install_claude_reference_creates_reference_skill(self) -> None:
        """Verify that install_claude_reference writes a lightweight reference skill."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        self.installer.install_skill(skill_rel_path, self.project_dir)

        success = self.installer.install_claude_reference(self.skill_name, self.project_dir)

        self.assertTrue(success)

        target_path = os.path.join(self.project_dir, ".claude", "skills", self.skill_name, "SKILL.md")
        self.assertTrue(os.path.isfile(target_path))

        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        # test-skill defaults to shared → reference points to .agents/skills/
        self.assertIn("Use the installed Gemini skill", content)
        self.assertIn(f".agents/skills/{self.skill_name}/SKILL.md", content)
        with open(os.path.join(self.project_dir, ".gitignore"), "r", encoding="utf-8") as f:
            gitignore = f.read()
        self.assertIn(f".claude/skills/{self.skill_name}/", gitignore)

    def test_uninstall_skill_removes_managed_artifacts(self) -> None:
        """Verify uninstall removes agents/Claude artifacts and refreshes gitignore."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        self.installer.install_skill(skill_rel_path, self.project_dir)
        self.installer.install_claude_reference(self.skill_name, self.project_dir)

        success = self.installer.uninstall_skill(self.skill_name, self.project_dir)

        self.assertTrue(success)
        self.assertFalse(os.path.exists(os.path.join(self.project_dir, ".agents", "skills", self.skill_name)))
        self.assertFalse(os.path.exists(os.path.join(self.project_dir, ".claude", "skills", self.skill_name)))
        with open(os.path.join(self.project_dir, ".gitignore"), "r", encoding="utf-8") as f:
            gitignore = f.read()
        self.assertNotIn(f".agents/skills/{self.skill_name}/", gitignore)
        self.assertNotIn(f".claude/skills/{self.skill_name}/", gitignore)

    def test_uninstall_skill_ignores_unmanaged_skill(self) -> None:
        """Verify uninstall does not remove unmanaged local skills."""
        unmanaged_path = os.path.join(self.project_dir, ".gemini", "skills", "local-only")
        os.makedirs(unmanaged_path, exist_ok=True)
        with open(os.path.join(unmanaged_path, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("# Local Only")

        success = self.installer.uninstall_skill("local-only", self.project_dir)

        self.assertFalse(success)
        self.assertTrue(os.path.isdir(unmanaged_path))

    def test_uninstall_skill_returns_false_when_a_managed_artifact_is_locked(self) -> None:
        """Verify uninstall fails gracefully without crashing when a managed artifact cannot be removed."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        self.installer.install_skill(skill_rel_path, self.project_dir)

        # test-skill defaults to shared → .agents/skills/
        agents_path = os.path.join(self.project_dir, ".agents", "skills", self.skill_name)

        original_remove = self.installer._remove_directory_tree

        def failing_remove(path: str) -> None:
            if path == agents_path:
                raise PermissionError("locked")
            original_remove(path)

        self.installer._remove_directory_tree = failing_remove  # type: ignore[method-assign]
        try:
            success = self.installer.uninstall_skill(self.skill_name, self.project_dir)
        finally:
            self.installer._remove_directory_tree = original_remove  # type: ignore[method-assign]

        self.assertFalse(success)
        self.assertTrue(os.path.isdir(agents_path))

    @unittest.skipUnless(os.name == "nt", "Windows junction tests only run on Windows")
    def test_uninstall_skill_removes_legacy_junction_artifact(self) -> None:
        """Verify uninstall removes a managed skill even if its payload is a junction."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        self.installer.install_skill(skill_rel_path, self.project_dir)

        # test-skill defaults to shared → .agents/skills/
        target_path = os.path.join(self.project_dir, ".agents", "skills", self.skill_name)
        shutil.rmtree(target_path)

        import subprocess

        subprocess.run(
            ["cmd", "/c", "mklink", "/J", target_path, os.path.abspath(self.skill_src_path)],
            check=True,
            capture_output=True,
            text=True,
        )

        success = self.installer.uninstall_skill(self.skill_name, self.project_dir)

        self.assertTrue(success)
        self.assertFalse(os.path.exists(target_path))

    @unittest.skipUnless(os.name == "nt", "Windows junction tests only run on Windows")
    def test_transition_from_junction_to_copy(self) -> None:
        """Verify that a legacy junction is correctly replaced by a copy."""
        skill_rel_path = f"{self.skill_cat}/{self.skill_name}"
        # test-skill defaults to shared → .agents/skills/
        target_skills_dir = os.path.join(self.project_dir, ".agents", "skills")
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
