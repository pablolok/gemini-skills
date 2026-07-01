"""Post-installation hook for review-optimization skill.
Integrates the skill into the project's Conductor workflow.
"""

import os
import sys

def integrate_into_workflow(target_project_path: str):
    """Detect conductor/workflow.md and insert the optimization audit step."""
    workflow_path = os.path.join(target_project_path, "conductor", "workflow.md")
    
    if not os.path.exists(workflow_path):
        print(f"No Conductor workflow found at {workflow_path}. Skipping integration.")
        return

    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if already integrated
    if "review-optimization" in content or "review_optimization" in content:
        print("Review optimization already integrated into workflow.")
        return

    print(f"Integrating review-optimization into {workflow_path}...")
    
    # We want to insert it after Step 3.2 in Phase Completion Verification
    # and before Step 4.
    target_marker = "-   **Step 3.2: Compliance Audit Orchestration:**"
    new_step = """
    -   **Step 3.3: Post-Execution Review & Optimization:**
        -   You **must** invoke the `review-optimization` skill to analyze the phase's execution path, audit skill efficiency, and receive workflow optimization advice.
        -   Follow the interactive recommendations provided by the skill to refine the workflow or update existing skills."""
    
    if target_marker in content:
        # Find where Step 3.2 ends. It's usually after the remediation bullet.
        # We'll insert it right before Step 4 or Step 3.3 if it exists (it doesn't yet).
        search_marker = "remediation steps within the orchestrator if any violations are found."
        insertion_point = content.find(search_marker, content.find(target_marker))
        
        if insertion_point != -1:
            end_of_line = content.find("\n", insertion_point)
            if end_of_line != -1:
                updated_content = content[:end_of_line+1] + new_step + content[end_of_line+1:]
                
                with open(workflow_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print("Successfully updated workflow.md.")
                return

    print("Could not find exact insertion point in workflow.md. Manual integration required.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_project = sys.argv[1]
        integrate_into_workflow(target_project)
    else:
        print("Usage: python post_install.py <target_project_path>")
