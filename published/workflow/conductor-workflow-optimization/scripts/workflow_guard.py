"""Detect common Conductor workflow drift patterns."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence


DEFAULT_FORBIDDEN_TOOLS = ("exit_plan_mode",)
DEFAULT_TARGET_DIRS = ("conductor", "skills", ".gemini")
DEFAULT_EXTENSIONS = {".md", ".toml", ".json", ".py", ".yaml", ".yml"}
EXCLUDED_PATH_PARTS = ("conductor-workflow-optimization",)


@dataclass(frozen=True)
class Finding:
    """A workflow drift finding."""

    kind: str
    path: str
    line: int
    message: str
    snippet: str


def iter_target_files(root: str, target_dirs: Sequence[str]) -> Iterable[str]:
    """Yield candidate workflow files under known workflow directories."""
    seen: set[str] = set()
    for relative_dir in target_dirs:
        base_dir = os.path.join(root, relative_dir)
        if not os.path.exists(base_dir):
            continue
        for current_root, _dirnames, filenames in os.walk(base_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() not in DEFAULT_EXTENSIONS:
                    continue
                full_path = os.path.join(current_root, filename)
                if any(part in full_path for part in EXCLUDED_PATH_PARTS):
                    continue
                if full_path not in seen:
                    seen.add(full_path)
                    yield full_path


def find_line_number(content: str, offset: int) -> int:
    """Convert a string offset into a 1-based line number."""
    return content.count("\n", 0, offset) + 1


def detect_forbidden_tools(path: str, content: str, forbidden_tools: Sequence[str]) -> list[Finding]:
    """Detect explicit forbidden tool references."""
    findings: list[Finding] = []
    for tool_name in forbidden_tools:
        pattern = re.compile(rf"\b{re.escape(tool_name)}\b")
        for match in pattern.finditer(content):
            line = find_line_number(content, match.start())
            findings.append(
                Finding(
                    kind="forbidden_tool",
                    path=path,
                    line=line,
                    message=f"Forbidden or stale tool reference '{tool_name}' detected.",
                    snippet=content.splitlines()[line - 1].strip(),
                )
            )
    return findings


def detect_plan_mode_gaps(path: str, content: str) -> list[Finding]:
    """Detect plan-mode guidance that omits the concrete finish/cancel actions."""
    lowered = content.lower()
    if "plan mode" not in lowered and "planning workflow" not in lowered:
        return []
    if "finish_plan" in content and "cancel_plan" in content:
        return []
    transition_pattern = re.compile(
        r"(?i)(exit|leave|stop|end|close)\s+(the\s+)?(current\s+)?(plan mode|planning workflow)"
    )
    findings: list[Finding] = []
    for match in transition_pattern.finditer(content):
        line = find_line_number(content, match.start())
        findings.append(
            Finding(
                kind="plan_mode_gap",
                path=path,
                line=line,
                message="Plan-mode transition guidance found without naming both `finish_plan` and `cancel_plan`.",
                snippet=content.splitlines()[line - 1].strip(),
            )
        )
        break
    return findings


def detect_binary_confirmation_prompts(path: str, content: str) -> list[Finding]:
    """Detect confirmation prompts that should preserve a free-text path."""
    patterns = (
        r"(?i)type\s+['\"]?yes['\"]?\s+to\s+confirm",
        r"(?i)\byes/no\b",
        r"(?i)\brespond\s+yes\s+or\s+no\b",
    )
    findings: list[Finding] = []
    for raw_pattern in patterns:
        match = re.search(raw_pattern, content)
        if not match:
            continue
        line = find_line_number(content, match.start())
        findings.append(
            Finding(
                kind="binary_confirmation_prompt",
                path=path,
                line=line,
                message="Binary confirmation prompt detected. Prefer `yes`, `no`, or free-text feedback.",
                snippet=content.splitlines()[line - 1].strip(),
            )
        )
        break
    return findings


def collect_findings(root: str, forbidden_tools: Sequence[str], target_dirs: Sequence[str]) -> list[Finding]:
    """Scan the repository for workflow drift findings."""
    findings: list[Finding] = []
    for path in iter_target_files(root, target_dirs):
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
        findings.extend(detect_forbidden_tools(path, content, forbidden_tools))
        findings.extend(detect_plan_mode_gaps(path, content))
        findings.extend(detect_binary_confirmation_prompts(path, content))
    return sorted(findings, key=lambda item: (item.path, item.line, item.kind))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--forbid",
        action="append",
        default=[],
        help="Additional forbidden tool name. Repeatable.",
    )
    parser.add_argument(
        "--target-dir",
        action="append",
        default=[],
        help="Additional top-level directory to scan. Repeatable.",
    )
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the workflow guard CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    forbidden_tools = list(dict.fromkeys([*DEFAULT_FORBIDDEN_TOOLS, *args.forbid]))
    target_dirs = list(dict.fromkeys([*DEFAULT_TARGET_DIRS, *args.target_dir]))
    findings = collect_findings(root, forbidden_tools, target_dirs)

    if args.json:
        payload = {
            "root": root,
            "finding_count": len(findings),
            "findings": [asdict(item) for item in findings],
        }
        print(json.dumps(payload, indent=2))
    elif findings:
        print(f"Detected {len(findings)} workflow drift finding(s) under {root}:")
        for finding in findings:
            relative_path = os.path.relpath(finding.path, root)
            print(
                f"- [{finding.kind}] {relative_path}:{finding.line} {finding.message}\n"
                f"  {finding.snippet}"
            )
    else:
        print(f"No workflow drift findings detected under {root}.")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
