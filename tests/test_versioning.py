"""Tests for SemVer version comparison."""

import unittest
from versioning import VersionComparator

class TestVersionComparator(unittest.TestCase):
    """Test suite for VersionComparator."""

    def test_parse_version(self) -> None:
        """Verify parsing of valid SemVer strings."""
        self.assertEqual(VersionComparator.parse_version("1.0.0"), (1, 0, 0))
        self.assertEqual(VersionComparator.parse_version("2.15.3"), (2, 15, 3))
        self.assertEqual(VersionComparator.parse_version("0.1.0-alpha"), (0, 1, 0))

    def test_parse_version_invalid(self) -> None:
        """Verify handling of invalid SemVer strings."""
        with self.assertRaises(ValueError):
            VersionComparator.parse_version("1.0")
        with self.assertRaises(ValueError):
            VersionComparator.parse_version("v1.0.0")
        with self.assertRaises(ValueError):
            VersionComparator.parse_version("abc")

    def test_is_newer(self) -> None:
        """Verify comparison logic."""
        self.assertTrue(VersionComparator.is_newer("1.0.0", "1.0.1"))
        self.assertTrue(VersionComparator.is_newer("1.0.0", "1.1.0"))
        self.assertTrue(VersionComparator.is_newer("1.0.0", "2.0.0"))
        
        self.assertFalse(VersionComparator.is_newer("1.0.1", "1.0.0"))
        self.assertFalse(VersionComparator.is_newer("1.1.0", "1.0.0"))
        self.assertFalse(VersionComparator.is_newer("2.0.0", "1.0.0"))
        self.assertFalse(VersionComparator.is_newer("1.0.0", "1.0.0"))

if __name__ == "__main__":
    unittest.main()
