"""Interactive launcher for skill-manager install and uninstall flows."""

from __future__ import annotations

import logging
import typing

from install import get_cli_ask_user


def _mode_prompt() -> typing.Dict[str, typing.Any]:
    return {
        "questions": [{
            "header": "Choose Mode",
            "question": "Which skill-manager flow would you like to run?",
            "banner_subtitle": "Skill-Manager",
            "close_label": "manager",
            "type": "choice",
            "multiSelect": False,
            "options": [
                {
                    "label": "install",
                    "description": "Open the installer to add or update managed skills.",
                },
                {
                    "label": "uninstall",
                    "description": "Open the uninstaller to remove managed skills.",
                },
            ],
        }]
    }

def main() -> None:
    """Launch the installer or uninstaller from one shared UI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("skill_manager")
    logger.info("=== Gemini Skill Manager ===")

    ask_user_fn = get_cli_ask_user()
    response = ask_user_fn(_mode_prompt())
    answer = ""
    if isinstance(response, dict):
        answer = str(response.get("answers", {}).get("0", "")).strip().lower()

    if answer == "install":
        import install as install_module

        install_module.main()
        return
    if answer == "uninstall":
        import uninstall as uninstall_module

        uninstall_module.main()
        return

    logger.info("No skill-manager flow selected.")
    print("No skill-manager flow selected.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        logging.getLogger("skill_manager").info("User closed the manager.")
        raise SystemExit(130)
