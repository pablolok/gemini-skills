"""Test suite for verifying the integration of skills within the project workflow."""

import unittest
import os
from typing import List


class TestWorkflowIntegration(unittest.TestCase):
    """Test suite for verifying the integration of skills within the project workflow."""

    WORKFLOW_PATH: str = os.path.join("conductor", "workflow.md")

    @classmethod
    def setUpClass(cls) -> None:
        """Verify that the workflow file exists before running tests."""
        if not os.path.exists(cls.WORKFLOW_PATH):
            raise FileNotFoundError(f"Workflow file not found at {cls.WORKFLOW_PATH}")

    def test_review_optimization_in_checkpoint_protocol(self) -> None:
        """Verify that review-optimization skill is mentioned in the checkpoint protocol."""
        with open(self.WORKFLOW_PATH, "r", encoding="utf-8") as f:
            content: str = f.read()
            
            # Check for the Phase Completion Verification section
            section_header: str = "## Phase Completion Verification and Checkpointing Protocol"
            section_start: int = content.find(section_header)
            self.assertNotEqual(section_start, -1, f"Section '{section_header}' not found in workflow.md")
            
            checkpoint_section: str = content[section_start:]
            
            # Verify the skill invocation
            self.assertIn("review-optimization", checkpoint_section, "review-optimization skill must be mentioned in the checkpoint protocol")
            
            # Verify it's in step 3.3
            self.assertIn("Step 3.3: Post-Execution Review & Optimization", checkpoint_section)
            
            # Verify mandatory language
            self.assertIn("You **must** invoke the `review-optimization` skill", checkpoint_section)

    def test_checkpoint_protocol_steps(self) -> None:
        """Verify the integrity and sequence of the checkpoint protocol steps."""
        with open(self.WORKFLOW_PATH, "r", encoding="utf-8") as f:
            content: str = f.read()
            
            # Verify existence of key protocol elements
            mandatory_elements: List[str] = [
                "git diff --name-only <previous_checkpoint_sha> HEAD",
                "npm test",
                "compliance-audit-orchestrator",
                "review-optimization",
                "Propose a Detailed, Actionable Manual Verification Plan",
                "Create Checkpoint Commit",
                "git notes add -f"
            ]
            
            for element in mandatory_elements:
                self.assertIn(element, content, f"Mandatory protocol element '{element}' missing from workflow.md")
