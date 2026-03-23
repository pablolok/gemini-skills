"""Runtime helpers for the installed skill-manager integration."""

from __future__ import annotations

import importlib
import json
import logging
import os
import sys
from typing import Any, Callable, Dict, List


LOGGER = logging.getLogger("skill_manager_runtime")


def project_root() -> str:
    return os.getcwd()


def runtime_config_path(root: str | None = None) -> str:
    base = root or project_root()
    return os.path.join(base, ".gemini", "skills", "skill-manager", "runtime_config.json")


def load_runtime_config(root: str | None = None) -> Dict[str, Any]:
    config_path = runtime_config_path(root)
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_source_repo(root: str | None = None) -> str | None:
    env_override = os.environ.get("GEMINI_SKILLS_REPO")
    if env_override and os.path.exists(env_override):
        return os.path.abspath(env_override)

    config = load_runtime_config(root)
    source_repo_root = config.get("source_repo_root")
    if source_repo_root and os.path.exists(source_repo_root):
        return os.path.abspath(source_repo_root)

    return None


def resolve_published_dir(root: str | None = None) -> str | None:
    source_repo_root = resolve_source_repo(root)
    if not source_repo_root:
        return None

    published_dir = os.path.join(source_repo_root, "published")
    if os.path.exists(published_dir):
        return published_dir

    return None


def import_installer(source_repo_root: str) -> Any:
    normalized = os.path.abspath(source_repo_root)
    if normalized not in sys.path:
        sys.path.insert(0, normalized)
    return importlib.import_module("install")


def build_installer(
    root: str | None = None,
    ask_user_fn: Callable[..., Any] | None = None,
    logger: logging.Logger | None = None,
) -> Any:
    published_dir = resolve_published_dir(root)
    if not published_dir:
        raise FileNotFoundError("Could not locate the gemini-skills published directory.")

    installer_module = import_installer(os.path.dirname(published_dir))
    ask_user = ask_user_fn or (lambda *_args, **_kwargs: {"answers": {"0": []}})
    return installer_module.SkillInstaller(published_dir, ask_user, logger or LOGGER)


def check_updates(root: str | None = None) -> List[Dict[str, str]]:
    target_root = root or project_root()
    installer = build_installer(target_root)
    return installer.check_for_updates(target_root)


def apply_updates(root: str | None = None) -> List[Dict[str, str]]:
    target_root = root or project_root()
    installer = build_installer(target_root)
    updates = installer.check_for_updates(target_root)
    applied: List[Dict[str, str]] = []

    for update in updates:
        if installer.install_skill(update["rel_path"], target_root):
            applied.append(update)

    return applied


def format_updates(updates: List[Dict[str, str]]) -> str:
    if not updates:
        return "All installed Gemini skills are up to date."

    lines = [f"Found {len(updates)} update(s):"]
    for update in updates:
        lines.append(f"- {update['name']}: {update['installed']} -> {update['latest']}")
    return "\n".join(lines)
