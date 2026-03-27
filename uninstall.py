"""Interactive Gemini Skill Uninstaller.
Allows users to uninstall skill-manager-managed skills from the current project.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
import typing

from install import SkillSelector, get_cli_ask_user


def _load_runtime_module():
    runtime_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "skills",
        "skill-manager",
        "scripts",
        "runtime.py",
    )
    spec = importlib.util.spec_from_file_location("skill_manager_runtime", runtime_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load runtime module from {runtime_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNTIME = _load_runtime_module()


def build_uninstall_options(
    managed_skills: typing.Sequence[typing.Mapping[str, str]],
    available_skill_paths: typing.Sequence[str],
) -> typing.Dict[str, typing.List[str]]:
    """Convert managed installed skills into a selector-compatible category map."""
    category_lookup: typing.Dict[str, str] = {}
    for skill_path in available_skill_paths:
        if "/" not in skill_path:
            continue
        category, skill_name = skill_path.split("/", 1)
        skill_name = skill_name.strip()
        if skill_name:
            category_lookup[skill_name] = category.strip() or "managed"

    grouped: typing.Dict[str, typing.List[str]] = {}
    for item in managed_skills:
        skill_name = str(item.get("name", "")).strip()
        if not skill_name:
            continue
        category = category_lookup.get(skill_name, "managed")
        grouped.setdefault(category, []).append(skill_name)

    return {
        category: sorted(set(skill_names))
        for category, skill_names in grouped.items()
        if skill_names
    }


def main() -> None:
    """Run the CLI entry point for interactive uninstall selection."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("skill_uninstaller")
    logger.info("=== Gemini Skill Uninstaller ===")

    target_project = os.getcwd()
    if not os.access(target_project, os.W_OK):
        logger.error("Target project directory is not writable: %s", target_project)
        sys.exit(1)

    ask_user_fn = get_cli_ask_user()
    managed_installed = RUNTIME.list_managed_installed_skills(target_project)
    available = build_uninstall_options(
        managed_installed,
        RUNTIME.list_available_skill_paths(target_project),
    )

    if not available:
        logger.info("No managed skills found to uninstall.")
        print("No managed skills found to uninstall.")
        return

    installed_versions = {
        item["name"]: item.get("version", "unknown")
        for item in managed_installed
        if item.get("name")
    }
    selector = SkillSelector(ask_user_fn)
    selected, action = selector.select_skills_with_action(
        available,
        installed_versions,
        [],
        header="Select Skills",
        question_text="Which managed skills would you like to uninstall?",
        banner_subtitle="Skill-Manager Uninstaller",
        close_label="uninstaller",
        description_formatter=lambda category, skill, status: (
            f"Managed {category} skill: {skill}{status}"
        ),
        switch_action={
            "key": "BACKSPACE",
            "keys": ["\x08", "\x7f", "BACKSPACE"],
            "label": "go back to Skill-Manager",
            "action": "back_to_manager",
            "aliases": ["back", "backspace"],
        },
    )
    if action == "back_to_manager":
        import manage as manage_module

        manage_module.main()
        return
    selected_names = [os.path.basename(skill_path) for skill_path in selected]

    removed = RUNTIME.uninstall_named_skills(selected_names, target_project) if selected_names else []

    if not selected_names:
        logger.info("No skills selected.")
        print("No skills selected.")
        return

    if not removed:
        logger.info("No skills were removed.")
        print("No skills were removed.")
        return

    logger.info("Removed %s managed skill(s).", len(removed))
    print(f"Removed {len(removed)} managed skill(s):")
    for skill_name in removed:
        print(f"- {skill_name}")
    print("Run /skills reload and /commands reload if Gemini CLI is already open.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        logging.getLogger("skill_uninstaller").info("User closed the uninstaller.")
        sys.exit(130)
