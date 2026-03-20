import unittest
import os

class TestWorkflowIntegration(unittest.TestCase):
    WORKFLOW_PATH = "conductor/workflow.md"

    def test_review_optimization_in_checkpoint_protocol(self):
        """Verify that review-optimization skill is mentioned in the checkpoint protocol."""
        self.assertTrue(os.path.exists(self.WORKFLOW_PATH), f"Workflow file not found at {self.WORKFLOW_PATH}")

        with open(self.WORKFLOW_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            # Check if it's in the Phase Completion Verification and Checkpointing Protocol section
            section_start = content.find("## Phase Completion Verification and Checkpointing Protocol")
            self.assertNotEqual(section_start, -1, "Checkpoint protocol section not found in workflow.md")
            
            checkpoint_section = content[section_start:]
            self.assertIn("review-optimization", checkpoint_section, "review-optimization skill must be mentioned in the checkpoint protocol")

if __name__ == "__main__":
    unittest.main()
