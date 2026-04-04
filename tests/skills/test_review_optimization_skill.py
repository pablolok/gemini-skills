"""Test suite for verifying the structure of the review-optimization skill."""

import os
import unittest
from typing import Dict, List


class TestReviewOptimizationSkill(unittest.TestCase):
    """Test suite for verifying the review-optimization skill."""

    SKILL_PATH = os.path.join("skills", "review-optimization", "SKILL.md")

    @classmethod
    def setUpClass(cls) -> None:
        """Verify that the skill file exists before running tests."""
        if not os.path.exists(cls.SKILL_PATH):
            raise FileNotFoundError(f"Skill file not found at {cls.SKILL_PATH}")

    def test_skill_file_exists(self) -> None:
        """Verify that the skill's SKILL.md file exists."""
        self.assertTrue(
            os.path.exists(self.SKILL_PATH),
            f"Skill file not found at {self.SKILL_PATH}"
        )

    def test_skill_frontmatter(self) -> None:
        """Verify that the skill file has correct frontmatter."""
        with open(self.SKILL_PATH, "r", encoding="utf-8") as f:
            content: str = f.read()
            if not content.startswith("---"):
                self.fail("Skill file must start with frontmatter separator")
            
            # Extract frontmatter
            parts: List[str] = content.split("---")
            if len(parts) < 3:
                self.fail(
                    "Skill file frontmatter must be enclosed by separators"
                )
            
            frontmatter_lines: List[str] = parts[1].strip().split("\n")
            frontmatter_dict: Dict[str, str] = {}
            for line in frontmatter_lines:
                if ":" in line:
                    key: str
                    value: str
                    key, value = line.split(":", 1)
                    frontmatter_dict[key.strip()] = value.strip()
            
            self.assertEqual(
                frontmatter_dict.get("name"),
                "review-optimization",
                "Skill name must be 'review-optimization'"
            )
            self.assertIn("description", frontmatter_dict)

    def test_skill_sections(self) -> None:
        """Verify that the skill file contains mandatory sections."""
        with open(self.SKILL_PATH, "r", encoding="utf-8") as f:
            content: str = f.read()
            self.assertIn("# Post-Execution Review & Optimization", content)
            self.assertIn("## Workflow Optimization Logic", content)
            self.assertIn("## Analysis Scope", content)
            self.assertIn("## Interactive Remediation", content)


def main() -> None:
    """Main function to run tests."""
    unittest.main()


if __name__ == "__main__":
    main()
