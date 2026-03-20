import unittest
import os

class TestReviewOptimizationSkill(unittest.TestCase):
    SKILL_PATH = os.path.join("skills", "review-optimization", "SKILL.md")

    def test_skill_file_exists(self):
        """Verify that the skill's SKILL.md file exists."""
        self.assertTrue(os.path.exists(self.SKILL_PATH), f"Skill file not found at {self.SKILL_PATH}")

    def test_skill_frontmatter(self):
        """Verify that the skill file has correct frontmatter."""
        if not os.path.exists(self.SKILL_PATH):
            self.skipTest("Skill file does not exist")

        with open(self.SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.startswith("---"):
                self.fail("Skill file must start with frontmatter separator '---'")
            
            # Extract frontmatter
            parts = content.split("---")
            if len(parts) < 3:
                self.fail("Skill file frontmatter must be enclosed by '---' separators")
            
            frontmatter_lines = parts[1].strip().split("\n")
            frontmatter_dict = {}
            for line in frontmatter_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter_dict[key.strip()] = value.strip()
            
            self.assertEqual(frontmatter_dict.get("name"), "review-optimization", "Skill name must be 'review-optimization'")
            self.assertIn("description", frontmatter_dict, "Skill must have a description")

    def test_skill_sections(self):
        """Verify that the skill file contains mandatory sections."""
        if not os.path.exists(self.SKILL_PATH):
            self.skipTest("Skill file does not exist")

        with open(self.SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# Post-Execution Review & Optimization", content)
            self.assertIn("## Workflow Optimization Logic", content)
            self.assertIn("## Analysis Scope", content)
            self.assertIn("## Interactive Remediation", content)

if __name__ == "__main__":
    unittest.main()
