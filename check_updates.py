"""Standalone script to check for Gemini skill updates."""

import os
import sys
import logging
from install import SkillInstaller, manual_ask_user

def main(ask_user_fn: typing.Optional[typing.Callable] = None) -> None:
    """Run the update check flow."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("update_checker")
    
    logger.info("=== Gemini Skill Update Checker ===")
    
    # Locate published directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    published_dir = os.path.join(script_dir, "published")
    
    if not os.path.exists(published_dir):
        logger.error(f"Published skills directory not found: {published_dir}")
        sys.exit(1)
        
    ask_fn = ask_user_fn or manual_ask_user
    installer = SkillInstaller(published_dir, ask_fn, logger)
    target_project = os.getcwd()
    
    logger.info(f"Checking for updates in: {target_project}")
    updates = installer.check_for_updates(target_project)
    
    if not updates:
        logger.info("All skills are up to date.")
        return

    logger.info(f"\nFound {len(updates)} update(s) available:")
    for update in updates:
        logger.info(f"- {update['name']}: {update['installed']} -> {update['latest']}")
    
    # Prompt for update
    response = ask_fn({
        "questions": [{
            "header": "Update Skills",
            "question": "Would you like to update these skills now?",
            "type": "choice",
            "options": [
                {"label": "Yes", "description": "Update all available skills"},
                {"label": "No", "description": "Do nothing"}
            ]
        }]
    })
    
    if "answers" in response and response["answers"]["0"] == ["Yes"]:
        logger.info("\nUpdating skills...")
        for update in updates:
            installer.install_skill(update['rel_path'], target_project)
        logger.info("\nAll updates completed successfully.")
    else:
        logger.info("Update cancelled.")

if __name__ == "__main__":
    main()
