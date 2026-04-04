"""Tests for metadata.json parsing and validation."""

import unittest
import os
import json
from install import SkillInstaller

class TestMetadataParsing(unittest.TestCase):
    """Test suite for skill metadata parsing."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.published_dir = "published"
        self.mock_ask_user = lambda x: {}
        self.installer = SkillInstaller(self.published_dir, self.mock_ask_user)

    def test_get_skill_metadata(self) -> None:
        """Verify that metadata can be correctly read for a skill."""
        # Using review-optimization as it's a known skill
        skill_rel_path = "audit/review-optimization"
        metadata = self.installer.get_skill_metadata(skill_rel_path)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["name"], "review-optimization")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertIn("description", metadata)

    def test_get_skill_metadata_missing(self) -> None:
        """Verify handling of missing metadata.json."""
        # We'll need a path that definitely doesn't have metadata.json
        # For now, let's just use a fake path
        metadata = self.installer.get_skill_metadata("non-existent/skill")
        self.assertIsNone(metadata)

if __name__ == "__main__":
    unittest.main()
