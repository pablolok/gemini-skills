"""Post-installation hook for conductor-workflow-optimization.
Integrates a workflow drift audit step into the project's Conductor workflow.
"""

from __future__ import annotations

import os
import sys


TARGET_MARKER = "-   **Step 3.3: Post-Execution Review & Optimization:**"
STEP_TITLE = "Step 3.4: Workflow Drift Audit"
NEW_STEP = """
    -   **Step 3.4: Workflow Drift Audit:**
        -   If Gemini emits an "unexpected tool call" error, references a missing tool, or the CLI help contradicts the workflow instructions, you **must** invoke the `conductor-workflow-optimization` skill before retrying.
        -   Use the skill to scan `conductor/workflow.md`, installed skills, policies, and generated commands for stale tool references and patch the narrowest broken workflow artifact first."""


def integrate_into_workflow(target_project_path: str) -> None:
    """Detect conductor/workflow.md and insert the workflow drift audit step."""
    workflow_path = os.path.join(target_project_path, "conductor", "workflow.md")

    if not os.path.exists(workflow_path):
        print(f"No Conductor workflow found at {workflow_path}. Skipping integration.")
        return

    with open(workflow_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    if "conductor-workflow-optimization" in content or STEP_TITLE in content:
        print("Conductor workflow optimization already integrated into workflow.")
        return

    step_index = content.find(TARGET_MARKER)
    if step_index == -1:
        print("Could not find the review optimization step in workflow.md. Manual integration required.")
        return

    error_handling_marker = "    -   **Error Handling:**"
    insertion_point = content.find(error_handling_marker, step_index)
    if insertion_point == -1:
        print("Could not find the error handling block in workflow.md. Manual integration required.")
        return

    updated_content = content[:insertion_point] + NEW_STEP + "\n" + content[insertion_point:]
    with open(workflow_path, "w", encoding="utf-8") as handle:
        handle.write(updated_content)

    print("Successfully updated workflow.md.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        integrate_into_workflow(sys.argv[1])
    else:
        print("Usage: python post_install.py <target_project_path>")
