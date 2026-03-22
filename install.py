"""Interactive Gemini Skill Installer.
Allows users to install official skills from the 'published/' directory into their projects.
"""

import os
import sys
import subprocess
import logging
import typing
import json
import shutil


class SkillSelector:
    """Handle skill selection via interactive prompt."""

    ask_user: typing.Callable

    def __init__(self, ask_user_fn: typing.Callable) -> None:
        """Initialize with an ask_user-compatible function."""
        self.ask_user = ask_user_fn

    def select_skills(
        self,
        available_skills: typing.Dict[str, typing.List[str]],
        installed_skills: typing.Optional[typing.Dict[str, str]] = None,
        updates: typing.Optional[typing.List[typing.Dict[str, str]]] = None
    ) -> typing.List[typing.List[str]]:
        """Prompt user to select skills from available categories with status info."""
        options: typing.List[typing.Dict[str, str]] = []
        installed = installed_skills or {}
        update_names = {u["name"] for u in (updates or [])}

        for category, skills in available_skills.items():
            for skill in skills:
                label = f"{category}/{skill}"
                status = ""
                if skill in update_names:
                    status = " [UPDATE AVAILABLE]"
                elif skill in installed:
                    status = f" [Installed v{installed[skill]}]"
                
                options.append({
                    "label": label,
                    "description": f"Official {category} skill: {skill}{status}"
                })

        if not options:
            return []

        response = self.ask_user({
            "questions": [{
                "header": "Select Skills",
                "question": "Which skills would you like to install or update?",
                "type": "choice",
                "multiSelect": True,
                "options": options
            }]
        })

        # Parse the standard tool response structure
        if isinstance(response, dict) and "answers" in response:
            return response["answers"]["0"]
        
        return []


class SkillInstaller:
    """Handle directory scanning and junction creation logic."""

    published_dir: str
    ask_user: typing.Callable
    logger: logging.Logger
    version_comparator: typing.Any

    def __init__(
        self,
        published_dir: str,
        ask_user_fn: typing.Callable,
        logger: typing.Optional[logging.Logger] = None,
        version_comparator: typing.Any = None
    ) -> None:
        """Initialize with paths and tools."""
        self.published_dir = os.path.abspath(published_dir)
        self.ask_user = ask_user_fn
        self.logger = logger or logging.getLogger("skill_installer")
        
        if version_comparator is None:
            from versioning import VersionComparator
            self.version_comparator = VersionComparator
        else:
            self.version_comparator = version_comparator

    def get_available_skills(self) -> typing.Dict[str, typing.List[str]]:
        """Scan the published directory for categories and skills."""
        available: typing.Dict[str, typing.List[str]] = {}
        if not os.path.exists(self.published_dir):
            return available

        for category in os.listdir(self.published_dir):
            cat_path = os.path.join(self.published_dir, category)
            if not os.path.isdir(cat_path):
                continue
            
            skills: typing.List[str] = []
            for skill in os.listdir(cat_path):
                skill_path = os.path.join(cat_path, skill)
                # Ensure it's a directory and not a hidden file/gitkeep
                if os.path.isdir(skill_path) and not skill.startswith("."):
                    skills.append(skill)
            
            if skills:
                available[category] = skills
        
        return available

    def get_skill_metadata(self, skill_rel_path: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Read and parse the metadata.json for a skill."""
        metadata_path = os.path.join(self.published_dir, skill_rel_path, "metadata.json")
        return self._read_metadata(metadata_path)

    def get_installed_skill_metadata(
        self,
        skill_name: str,
        target_project_path: str
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Read and parse the metadata.json for an installed skill."""
        metadata_path = os.path.join(target_project_path, ".gemini", "skills", skill_name, "metadata.json")
        return self._read_metadata(metadata_path)

    def _read_metadata(self, metadata_path: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Read and parse a metadata.json file."""
        if not os.path.exists(metadata_path):
            return None

        try:
            with open(metadata_path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error parsing metadata at '{metadata_path}': {e}")
            return None

    def check_for_updates(self, target_project_path: str) -> typing.List[typing.Dict[str, str]]:
        """Check all installed skills for available updates."""
        updates = []
        target_skills_dir = os.path.join(target_project_path, ".gemini", "skills")
        if not os.path.exists(target_skills_dir):
            return updates

        available_skills = self.get_available_skills()
        # Create a reverse map: skill_name -> rel_path
        name_to_rel = {}
        for cat, skills in available_skills.items():
            for s in skills:
                name_to_rel[s] = os.path.join(cat, s)

        for skill_name in os.listdir(target_skills_dir):
            skill_path = os.path.join(target_skills_dir, skill_name)
            if not os.path.isdir(skill_path):
                continue

            installed_meta = self.get_installed_skill_metadata(skill_name, target_project_path)
            if not installed_meta or "version" not in installed_meta:
                continue

            rel_path = name_to_rel.get(skill_name)
            if not rel_path:
                continue

            latest_meta = self.get_skill_metadata(rel_path)
            if not latest_meta or "version" not in latest_meta:
                continue

            if self.version_comparator.is_newer(installed_meta["version"], latest_meta["version"]):
                updates.append({
                    "name": skill_name,
                    "installed": installed_meta["version"],
                    "latest": latest_meta["version"],
                    "rel_path": rel_path
                })

        return updates

    def notify_updates(self, updates: typing.List[typing.Dict[str, str]]) -> None:
        """Log a notification message for available updates."""
        if not updates:
            return

        self.logger.info("\n[UPDATE AVAILABLE] Newer versions of some skills are available:")
        for update in updates:
            self.logger.info(f"  - {update['name']}: {update['installed']} -> {update['latest']}")
        self.logger.info("\nRun 'python install.py' or 'python check_updates.py' to update.\n")

    def install_skill(self, skill_rel_path: str, target_project_path: str) -> bool:
        """Install a skill by copying files to the target project."""
        source_path = os.path.join(self.published_dir, skill_rel_path)
        skill_name = os.path.basename(skill_rel_path)
        
        target_skills_dir = os.path.join(target_project_path, ".gemini", "skills")
        if not os.path.exists(target_skills_dir):
            os.makedirs(target_skills_dir)
            
        target_path = os.path.join(target_skills_dir, skill_name)
        
        if os.path.exists(target_path):
            self.logger.info(f"Skill '{skill_name}' already exists. Overwriting...")
            # Use a robust check for junctions and symlinks
            if self._is_link_or_junction(target_path):
                self._remove_junction(target_path)
            # shutil.copytree with dirs_exist_ok=True will handle existing directories

        self.logger.info(f"Installing skill '{skill_name}' via file copying...")
        try:
            self._copy_skill_files(os.path.abspath(source_path), os.path.abspath(target_path))
            self.logger.info(f"Successfully installed '{skill_name}'.")
            
            # Check for post-install hook
            hook_path = os.path.join(source_path, "post_install.py")
            if os.path.exists(hook_path):
                self._run_post_install_hook(hook_path, target_project_path)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to install '{skill_name}': {e}")
            return False

    def _is_link_or_junction(self, path: str) -> bool:
        """Check if a path is a symlink or a Windows directory junction."""
        if os.path.islink(path):
            return True
        
        if sys.platform == "win32":
            # On some Windows/Python versions, islink doesn't catch junctions.
            # Check for FILE_ATTRIBUTE_REPARSE_POINT (0x400)
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
                return attrs != -1 and bool(attrs & 0x400)
            except Exception:
                return False
        return False

    def _remove_junction(self, path: str) -> None:
        """Remove a directory junction or symlink."""
        if sys.platform == "win32":
            # os.rmdir is safe for junctions on Windows
            os.rmdir(path)
        else:
            os.remove(path)

    def _run_post_install_hook(self, hook_path: str, target_project_path: str) -> None:
        """Execute the post_install.py script for a skill."""
        self.logger.info(f"Running post-install hook: {os.path.basename(hook_path)}...")
        try:
            # Pass the target project path as an argument to the hook
            subprocess.run(
                [sys.executable, os.path.abspath(hook_path), os.path.abspath(target_project_path)],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info("Post-install hook completed successfully.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Post-install hook failed with exit code {e.returncode}")
            if e.stderr:
                self.logger.error(f"Error: {e.stderr.strip()}")
        except Exception as e:
            self.logger.error(f"Error running post-install hook: {e}")

    def _copy_skill_files(self, source: str, target: str) -> None:
        """Recursively copy skill files from source to target."""
        shutil.copytree(source, target, dirs_exist_ok=True)


def manual_ask_user(config: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """Provide a fallback interactive prompt for manual execution."""
    question = config["questions"][0]
    is_multi = question.get("multiSelect", False)
    
    print(f"\n{question['question']}")
    if is_multi:
        print("(You can select multiple options by separating numbers with spaces)")
    
    for i, opt in enumerate(question['options']):
        print(f"{i}: {opt['label']} - {opt['description']}")
    
    selection = input("\nEnter choice(s): ")
    indices: typing.List[int] = [
        int(x.strip()) for x in selection.split() 
        if x.strip().isdigit() and 0 <= int(x.strip()) < len(question['options'])
    ]
    
    if not is_multi and indices:
        indices = [indices[0]]
        
    return {"answers": {"0": [question['options'][i]['label'] for i in indices]}}


def main() -> None:
    """Run the CLI entry point for manual or agent execution."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("skill_installer")
    logger.info("=== Gemini Skill Installer ===")
    
    # In this repo, 'published' is relative to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    published_dir = os.path.join(script_dir, "published")
    
    if not os.path.exists(published_dir):
        logger.error(f"Published skills directory not found: {published_dir}")
        sys.exit(1)
    
    target_project = os.getcwd()
    if not os.access(target_project, os.W_OK):
        logger.error(f"Target project directory is not writable: {target_project}")
        sys.exit(1)

    # Run the installation flow
    installer = SkillInstaller(published_dir, manual_ask_user, logger)
    available = installer.get_available_skills()
    
    if not available:
        logger.info("No skills found to install.")
        return

    # Gather installation status for the selector
    updates = installer.check_for_updates(target_project)
    installed_skills = {}
    target_skills_dir = os.path.join(target_project, ".gemini", "skills")
    if os.path.exists(target_skills_dir):
        for skill_name in os.listdir(target_skills_dir):
            if os.path.isdir(os.path.join(target_skills_dir, skill_name)):
                meta = installer.get_installed_skill_metadata(skill_name, target_project)
                installed_skills[skill_name] = meta.get("version", "unknown") if meta else "unknown"

    selector = SkillSelector(manual_ask_user)
    selected = selector.select_skills(available, installed_skills, updates)
    
    for skill_path in selected:
        installer.install_skill(skill_path, target_project)


if __name__ == "__main__":
    main()
