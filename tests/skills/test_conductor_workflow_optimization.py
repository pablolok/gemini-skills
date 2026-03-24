"""Tests for conductor-workflow-optimization."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO


def _load_module(module_name: str, path: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


WORKFLOW_GUARD = _load_module(
    "conductor_workflow_guard",
    os.path.join("skills", "conductor-workflow-optimization", "scripts", "workflow_guard.py"),
)
POST_INSTALL = _load_module(
    "conductor_workflow_optimization_post_install",
    os.path.join("skills", "conductor-workflow-optimization", "post_install.py"),
)


class TestWorkflowGuard(unittest.TestCase):
    def test_collect_findings_detects_forbidden_tool_and_plan_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            conductor_dir = os.path.join(temp_dir, "conductor")
            os.makedirs(conductor_dir, exist_ok=True)
            workflow_path = os.path.join(conductor_dir, "workflow.md")
            with open(workflow_path, "w", encoding="utf-8") as handle:
                handle.write(
                    "# Workflow\n"
                    "To exit plan mode, call `exit_plan_mode`.\n"
                    "Please type 'yes' to confirm.\n"
                )

            findings = WORKFLOW_GUARD.collect_findings(
                temp_dir,
                ["exit_plan_mode"],
                ["conductor"],
            )

            kinds = {finding.kind for finding in findings}
            self.assertIn("forbidden_tool", kinds)
            self.assertIn("plan_mode_gap", kinds)
            self.assertIn("binary_confirmation_prompt", kinds)

    def test_main_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            conductor_dir = os.path.join(temp_dir, "conductor")
            os.makedirs(conductor_dir, exist_ok=True)
            workflow_path = os.path.join(conductor_dir, "workflow.md")
            with open(workflow_path, "w", encoding="utf-8") as handle:
                handle.write("Call `exit_plan_mode`.\n")

            buffer = StringIO()
            with redirect_stdout(buffer):
                exit_code = WORKFLOW_GUARD.main(["--root", temp_dir, "--json"])

            payload = json.loads(buffer.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertGreaterEqual(payload["finding_count"], 1)


class TestPostInstall(unittest.TestCase):
    def test_integrate_into_workflow_inserts_step_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow_dir = os.path.join(temp_dir, "conductor")
            os.makedirs(workflow_dir, exist_ok=True)
            workflow_path = os.path.join(workflow_dir, "workflow.md")
            with open(workflow_path, "w", encoding="utf-8") as handle:
                handle.write(
                    "    -   **Step 3.3: Post-Execution Review & Optimization:**\n"
                    "        -   You **must** invoke the `review-optimization` skill.\n"
                    "    -   **Error Handling:** Existing text.\n"
                )

            POST_INSTALL.integrate_into_workflow(temp_dir)
            POST_INSTALL.integrate_into_workflow(temp_dir)

            with open(workflow_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            self.assertIn("Step 3.4: Workflow Drift Audit", content)
            self.assertIn("conductor-workflow-optimization", content)
            self.assertEqual(content.count("Step 3.4: Workflow Drift Audit"), 1)
