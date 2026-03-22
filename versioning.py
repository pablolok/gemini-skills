"""SemVer version comparison logic."""

import re
import typing

class VersionComparator:
    """Handle Semantic Versioning (SemVer) comparison."""

    @staticmethod
    def parse_version(version_str: str) -> typing.Tuple[int, int, int]:
        """Parse a SemVer string into a numeric tuple (major, minor, patch)."""
        # Basic SemVer regex
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-.*)?$", version_str)
        if not match:
            raise ValueError(f"Invalid SemVer format: {version_str}")
        
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))

    @classmethod
    def is_newer(cls, current: str, latest: str) -> bool:
        """Return True if latest is newer than current."""
        try:
            curr_v = cls.parse_version(current)
        except ValueError:
            # If current is invalid, assume latest is newer if it is valid
            try:
                cls.parse_version(latest)
                return True
            except ValueError:
                return False

        try:
            late_v = cls.parse_version(latest)
            return late_v > curr_v
        except ValueError:
            return False
