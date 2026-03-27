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
import re


KeyReader = typing.Callable[[], str]
AskUserResponse = typing.Dict[str, typing.Any]
GITIGNORE_MARKER_START = "# >>> skill-manager managed workspace files >>>"
GITIGNORE_MARKER_END = "# <<< skill-manager managed workspace files <<<"
MANAGED_SKILL_MANIFEST = ".gemini/skill-manager-manifest.json"
GITIGNORE_ENTRIES = [
    ".gemini/commands/",
    ".gemini/settings.json",
    MANAGED_SKILL_MANIFEST,
]


def parse_selection_input(
    raw_selection: str,
    option_count: int,
    is_multi: bool,
) -> typing.List[int]:
    """Parse human-friendly selection input into zero-based indices."""
    if option_count <= 0:
        return []

    tokens = raw_selection.replace(",", " ").split()
    if not tokens:
        return []

    indices: typing.List[int] = []

    def add_index(index: int) -> None:
        if 0 <= index < option_count and index not in indices:
            indices.append(index)

    for token in tokens:
        lowered = token.lower()
        if is_multi and lowered in {"all", "*"}:
            return list(range(option_count))

        if "-" in token:
            start_text, end_text = token.split("-", 1)
            if start_text.isdigit() and end_text.isdigit():
                start_raw = int(start_text)
                end_raw = int(end_text)
                start = 0 if start_raw == 0 else start_raw - 1
                end = 0 if end_raw == 0 else end_raw - 1
                if start <= end:
                    for index in range(start, end + 1):
                        add_index(index)
                else:
                    for index in range(start, end - 1, -1):
                        add_index(index)
            continue

        if token.isdigit():
            raw_index = int(token)
            index = 0 if raw_index == 0 else raw_index - 1
            add_index(index)

    if not is_multi and indices:
        return [indices[0]]

    return indices


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
        
        # Create a mapping of update name to its update info dictionary
        update_map = {u["name"]: u for u in (updates or [])}

        for category, skills in available_skills.items():
            for skill in skills:
                label = f"{category}/{skill}"
                status = ""
                if skill in update_map:
                    update_info = update_map[skill]
                    status = f" [Update Available] ({update_info['installed']} -> {update_info['latest']})"
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


class TerminalMultiSelect:
    """Interactive multi-select widget for human CLI use."""

    def __init__(
        self,
        question: typing.Dict[str, typing.Any],
        input_stream: typing.Optional[typing.TextIO] = None,
        output_stream: typing.Optional[typing.TextIO] = None,
    ) -> None:
        self.question = question
        self.options = question.get("options", [])
        self.multi_select = bool(question.get("multiSelect", False))
        self.cursor = 0
        self.selected: typing.Set[int] = set()
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout

    def run(self, read_key: typing.Optional[KeyReader] = None) -> typing.List[str]:
        """Run the interactive selector and return selected labels."""
        if not self.options:
            return []

        if read_key is None:
            read_key = self._create_key_reader()

        self._hide_cursor()
        try:
            while True:
                self._render()
                key = read_key()

                if key in {"\x03", "CTRL_C"}:
                    raise KeyboardInterrupt
                if key in {"UP", "k"}:
                    self.cursor = (self.cursor - 1) % len(self.options)
                    continue
                if key in {"DOWN", "j"}:
                    self.cursor = (self.cursor + 1) % len(self.options)
                    continue
                if key == "SPACE":
                    if self.multi_select:
                        if self.cursor in self.selected:
                            self.selected.remove(self.cursor)
                        else:
                            self.selected.add(self.cursor)
                    else:
                        self.selected = {self.cursor}
                    continue
                if key in {"ENTER", "\r", "\n"}:
                    if not self.multi_select:
                        self.selected = {self.cursor}
                    break
                if key in {"a", "A"} and self.multi_select:
                    if len(self.selected) == len(self.options):
                        self.selected.clear()
                    else:
                        self.selected = set(range(len(self.options)))
                    continue
                if key in {"q", "Q", "ESC"}:
                    raise KeyboardInterrupt
        finally:
            self._clear_screen()
            self._show_cursor()

        return [self.options[index]["label"] for index in sorted(self.selected)]

    def _render(self) -> None:
        self._clear_screen()
        question = self.question.get("question", "Select option(s):")
        self.output_stream.write(f"{question}\n")
        if self.multi_select:
            self.output_stream.write("Use arrows, space to toggle, A to select all, Enter to confirm.\n\n")
        else:
            self.output_stream.write("Use arrows and Enter to confirm.\n\n")

        for index, option in enumerate(self.options):
            pointer = ">" if index == self.cursor else " "
            selected = "[x]" if index in self.selected else "[ ]"
            if not self.multi_select:
                selected = "(*)" if index in self.selected else "( )"
            description = option.get("description", "")
            self.output_stream.write(
                f"{pointer} {selected} {option['label']}\n    {description}\n"
            )
        self.output_stream.flush()

    def _clear_screen(self) -> None:
        self.output_stream.write("\x1b[2J\x1b[H")
        self.output_stream.flush()

    def _hide_cursor(self) -> None:
        self.output_stream.write("\x1b[?25l")
        self.output_stream.flush()

    def _show_cursor(self) -> None:
        self.output_stream.write("\x1b[?25h")
        self.output_stream.flush()

    def _create_key_reader(self) -> KeyReader:
        if sys.platform == "win32":
            return self._create_windows_key_reader()
        return self._create_posix_key_reader()

    def _create_windows_key_reader(self) -> KeyReader:
        import msvcrt

        def read_key() -> str:
            char = msvcrt.getwch()
            if char == "\x03":
                return "CTRL_C"
            if char in {"\r", "\n"}:
                return "ENTER"
            if char == " ":
                return "SPACE"
            if char == "\x1b":
                return "ESC"
            if char in {"\x00", "\xe0"}:
                special = msvcrt.getwch()
                return {
                    "H": "UP",
                    "P": "DOWN",
                }.get(special, special)
            return char

        return read_key

    def _create_posix_key_reader(self) -> KeyReader:
        import termios
        import tty

        input_stream = self.input_stream

        def read_key() -> str:
            fd = input_stream.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                char = input_stream.read(1)
                if char == "\x03":
                    return "CTRL_C"
                if char in {"\r", "\n"}:
                    return "ENTER"
                if char == " ":
                    return "SPACE"
                if char == "\x1b":
                    next_char = input_stream.read(1)
                    if next_char == "[":
                        arrow = input_stream.read(1)
                        return {
                            "A": "UP",
                            "B": "DOWN",
                        }.get(arrow, "ESC")
                    return "ESC"
                return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return read_key


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

    def codex_bridges_dir(self) -> str:
        """Resolve the source directory containing Codex bridge wrappers."""
        return os.path.join(os.path.dirname(self.published_dir), ".codex", "skills")

    def claude_reference_skill_content(self, skill_name: str, target_project_path: str) -> str:
        """Build a lightweight Claude reference skill that points at the installed Gemini skill."""
        metadata = self.get_installed_skill_metadata(skill_name, target_project_path) or {}
        description = metadata.get(
            "description",
            (
                f"Claude reference skill for the installed Gemini skill '{skill_name}'. "
                "Use the Gemini skill as the source of truth."
            ),
        )
        title = re.sub(r"[-_]+", " ", skill_name).strip().title() or skill_name
        return (
            "---\n"
            f"name: {skill_name}\n"
            f"description: {description}\n"
            "---\n\n"
            f"# {title} Reference\n\n"
            f"Use the installed Gemini skill at `.gemini/skills/{skill_name}/SKILL.md` as the source of truth.\n\n"
            "Workflow:\n\n"
            f"1. Read and follow `.gemini/skills/{skill_name}/SKILL.md`.\n"
            f"2. If that skill references scripts, metadata, or companion files, resolve them from `.gemini/skills/{skill_name}/`.\n"
            "3. Do not duplicate the Gemini implementation in `.claude/skills/`. This reference exists only so Claude can discover and invoke the installed Gemini skill guidance.\n"
        )

    def get_available_codex_bridges(self) -> typing.Set[str]:
        """Return skill names that have an explicit Codex bridge wrapper."""
        bridges_dir = self.codex_bridges_dir()
        if not os.path.isdir(bridges_dir):
            return set()

        bridges: typing.Set[str] = set()
        for item in os.listdir(bridges_dir):
            bridge_path = os.path.join(bridges_dir, item)
            skill_md = os.path.join(bridge_path, "SKILL.md")
            if os.path.isdir(bridge_path) and not item.startswith(".") and os.path.isfile(skill_md):
                bridges.add(item)
        return bridges

    def supports_codex_bridge(self, skill_name: str) -> bool:
        """Check whether a skill has a bridge wrapper intended for Codex."""
        return skill_name in self.get_available_codex_bridges()

    def supports_claude_reference(self, skill_name: str) -> bool:
        """Check whether a skill can get a generated Claude reference skill."""
        return bool(skill_name)

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

    def ensure_managed_gitignore_entries(self, target_project_path: str) -> bool:
        """Ensure the managed skill-manager gitignore block exists in the target project."""
        os.makedirs(target_project_path, exist_ok=True)
        gitignore_path = os.path.join(target_project_path, ".gitignore")
        manifest = self._load_managed_skill_manifest(target_project_path)
        skill_entries = self._build_managed_skill_ignore_entries(manifest)
        managed_lines = [
            GITIGNORE_MARKER_START,
            "# Ignore local Gemini workspace commands generated by skill-manager",
            GITIGNORE_ENTRIES[0],
            "# Ignore local Gemini workspace settings written by skill-manager",
            GITIGNORE_ENTRIES[1],
            "# Ignore the local skill-manager installation manifest",
            GITIGNORE_ENTRIES[2],
        ]
        if skill_entries:
            managed_lines.extend(
                [
                    "# Ignore skill directories installed and managed by skill-manager",
                    *skill_entries,
                ]
            )
        managed_lines.append(GITIGNORE_MARKER_END)
        managed_block = "\n".join(managed_lines)

        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as handle:
                content = handle.read()
        else:
            content = ""

        if GITIGNORE_MARKER_START in content and GITIGNORE_MARKER_END in content:
            start = content.index(GITIGNORE_MARKER_START)
            end = content.index(GITIGNORE_MARKER_END) + len(GITIGNORE_MARKER_END)
            before = content[:start].rstrip("\n")
            after = content[end:].lstrip("\n")
            sections = [section for section in (before, managed_block, after) if section]
            updated = "\n\n".join(sections) + "\n"
        else:
            updated = content.rstrip()
            if updated:
                updated += "\n\n"
            updated += managed_block + "\n"

        changed = updated != content
        with open(gitignore_path, "w", encoding="utf-8") as handle:
            handle.write(updated)
        return changed

    def _managed_skill_manifest_path(self, target_project_path: str) -> str:
        """Return the manifest path used to track skill-manager-installed skills."""
        return os.path.join(target_project_path, ".gemini", "skill-manager-manifest.json")

    def _load_managed_skill_manifest(
        self,
        target_project_path: str,
    ) -> typing.Dict[str, typing.List[str]]:
        """Load the local manifest of skills installed by skill-manager."""
        manifest_path = self._managed_skill_manifest_path(target_project_path)
        if not os.path.exists(manifest_path):
            return self._discover_managed_skills(target_project_path)

        try:
            with open(manifest_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            return {"gemini": [], "codex": [], "claude": []}

        manifest: typing.Dict[str, typing.List[str]] = {}
        for key in ("gemini", "codex", "claude"):
            values = payload.get(key, [])
            manifest[key] = sorted({str(value) for value in values if str(value).strip()})
        return manifest

    def _discover_managed_skills(
        self,
        target_project_path: str,
    ) -> typing.Dict[str, typing.List[str]]:
        """Bootstrap managed skills from currently installed local skill folders."""
        directories = {
            "gemini": os.path.join(target_project_path, ".gemini", "skills"),
            "codex": os.path.join(target_project_path, ".codex", "skills"),
            "claude": os.path.join(target_project_path, ".claude", "skills"),
        }
        discovered: typing.Dict[str, typing.List[str]] = {}
        for kind, directory in directories.items():
            if not os.path.isdir(directory):
                discovered[kind] = []
                continue
            names = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and not item.startswith("."):
                    names.append(item)
            discovered[kind] = sorted(names)
        return discovered

    def _write_managed_skill_manifest(
        self,
        target_project_path: str,
        manifest: typing.Dict[str, typing.List[str]],
    ) -> None:
        """Persist the local manifest of skills installed by skill-manager."""
        manifest_path = self._managed_skill_manifest_path(target_project_path)
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")

    def _register_managed_skill(
        self,
        target_project_path: str,
        kind: str,
        skill_name: str,
    ) -> None:
        """Record a skill directory as being installed by skill-manager."""
        manifest = self._load_managed_skill_manifest(target_project_path)
        current = set(manifest.get(kind, []))
        current.add(skill_name)
        manifest[kind] = sorted(current)
        self._write_managed_skill_manifest(target_project_path, manifest)

    def _build_managed_skill_ignore_entries(
        self,
        manifest: typing.Dict[str, typing.List[str]],
    ) -> typing.List[str]:
        """Build exact gitignore entries for skill directories managed by skill-manager."""
        entries: typing.List[str] = []
        base_paths = {
            "gemini": ".gemini/skills",
            "codex": ".codex/skills",
            "claude": ".claude/skills",
        }
        for kind in ("gemini", "codex", "claude"):
            base_path = base_paths[kind]
            for skill_name in manifest.get(kind, []):
                entries.append(f"{base_path}/{skill_name}/")
        return entries

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

    def install_codex_bridge(self, skill_name: str, target_project_path: str) -> bool:
        """Install a lightweight Codex bridge wrapper for a skill when available."""
        source_path = os.path.join(self.codex_bridges_dir(), skill_name)
        if not os.path.isfile(os.path.join(source_path, "SKILL.md")):
            self.logger.info(
                f"Skipping Codex bridge for '{skill_name}': no bridge wrapper is published for this skill."
            )
            return False

        target_skills_dir = os.path.join(target_project_path, ".codex", "skills")
        os.makedirs(target_skills_dir, exist_ok=True)
        target_path = os.path.join(target_skills_dir, skill_name)

        self.logger.info(f"Installing Codex bridge for '{skill_name}'...")
        try:
            self._copy_skill_files(os.path.abspath(source_path), os.path.abspath(target_path))
            self._register_managed_skill(target_project_path, "codex", skill_name)
            self.ensure_managed_gitignore_entries(target_project_path)
            self.logger.info(f"Successfully installed Codex bridge for '{skill_name}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to install Codex bridge for '{skill_name}': {e}")
            return False

    def install_claude_reference(self, skill_name: str, target_project_path: str) -> bool:
        """Install a lightweight Claude reference skill for an installed Gemini skill."""
        source_skill_path = os.path.join(target_project_path, ".gemini", "skills", skill_name, "SKILL.md")
        if not os.path.isfile(source_skill_path):
            self.logger.info(
                f"Skipping Claude reference for '{skill_name}': the Gemini skill is not installed in the target project."
            )
            return False

        target_skill_dir = os.path.join(target_project_path, ".claude", "skills", skill_name)
        os.makedirs(target_skill_dir, exist_ok=True)
        target_skill_path = os.path.join(target_skill_dir, "SKILL.md")

        self.logger.info(f"Installing Claude reference skill for '{skill_name}'...")
        try:
            content = self.claude_reference_skill_content(skill_name, target_project_path)
            with open(target_skill_path, "w", encoding="utf-8") as handle:
                handle.write(content)
            self._register_managed_skill(target_project_path, "claude", skill_name)
            self.ensure_managed_gitignore_entries(target_project_path)
            self.logger.info(f"Successfully installed Claude reference skill for '{skill_name}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to install Claude reference skill for '{skill_name}': {e}")
            return False

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
            self._register_managed_skill(target_project_path, "gemini", skill_name)
            self.ensure_managed_gitignore_entries(target_project_path)
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
            hook_env = os.environ.copy()
            hook_env["GEMINI_SKILLS_PUBLISHED_DIR"] = self.published_dir
            hook_env["GEMINI_SKILLS_REPO_ROOT"] = os.path.dirname(self.published_dir)
            # Pass the target project path as an argument to the hook
            subprocess.run(
                [sys.executable, os.path.abspath(hook_path), os.path.abspath(target_project_path)],
                check=True,
                capture_output=True,
                text=True,
                env=hook_env,
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
        print("(Select multiple with spaces or commas, ranges like 1-3, or 'all')")
    
    for i, opt in enumerate(question['options']):
        print(f"{i + 1}: {opt['label']} - {opt['description']}")
    
    try:
        selection = input("\nEnter choice(s): ")
    except KeyboardInterrupt:
        print("\nUser closed the installer.")
        raise

    indices = parse_selection_input(selection, len(question["options"]), is_multi)

    if question.get("type") == "choice" and not is_multi:
        answer: typing.Any = question["options"][indices[0]]["label"] if indices else ""
    else:
        answer = [question['options'][i]['label'] for i in indices]

    return {"answers": {"0": answer}}


def terminal_ask_user(config: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """Provide a richer terminal selector for direct CLI installs."""
    question = config["questions"][0]
    selector = TerminalMultiSelect(question)
    labels = selector.run()
    if question.get("type") == "choice" and not question.get("multiSelect", False):
        answer: typing.Any = labels[0] if labels else ""
    else:
        answer = labels
    return {"answers": {"0": answer}}


def prompt_for_codex_support(
    ask_user_fn: typing.Callable[[typing.Dict[str, typing.Any]], AskUserResponse],
    skill_names: typing.Sequence[str],
) -> typing.Set[str]:
    """Ask whether supported skills should also receive Codex bridge wrappers."""
    bridgeable = sorted(set(skill_names))
    if not bridgeable:
        return set()

    response = ask_user_fn({
        "questions": [{
            "header": "Codex Support",
            "question": (
                "Install matching Codex bridge wrappers in .codex/skills for supported selected skills?"
            ),
            "type": "choice",
            "multiSelect": False,
            "options": [
                {
                    "label": "yes",
                    "description": "Add lightweight Codex bridge wrappers for the supported selected skills.",
                },
                {
                    "label": "no",
                    "description": "Install only the Gemini skill payloads into .gemini/skills.",
                },
            ],
        }]
    })

    answer = ""
    if isinstance(response, dict):
        answer = str(response.get("answers", {}).get("0", "")).strip().lower()

    return set(bridgeable) if answer == "yes" else set()


def prompt_for_claude_support(
    ask_user_fn: typing.Callable[[typing.Dict[str, typing.Any]], AskUserResponse],
    skill_names: typing.Sequence[str],
) -> typing.Set[str]:
    """Ask whether selected skills should also receive Claude reference skills."""
    referenceable = sorted(set(skill_names))
    if not referenceable:
        return set()

    response = ask_user_fn({
        "questions": [{
            "header": "Claude Support",
            "question": (
                "Install generated Claude reference skills in .claude/skills for the selected skills?"
            ),
            "type": "choice",
            "multiSelect": False,
            "options": [
                {
                    "label": "yes",
                    "description": "Add lightweight Claude reference skills that point at the installed Gemini skills.",
                },
                {
                    "label": "no",
                    "description": "Install only the Gemini skill payloads into .gemini/skills.",
                },
            ],
        }]
    })

    answer = ""
    if isinstance(response, dict):
        answer = str(response.get("answers", {}).get("0", "")).strip().lower()

    return set(referenceable) if answer == "yes" else set()


def get_cli_ask_user(argv: typing.Optional[typing.Sequence[str]] = None) -> typing.Callable:
    """Choose the best interactive prompt for the current execution context."""
    args = set(argv or sys.argv[1:])
    if "--simple" in args or "--plain" in args:
        return manual_ask_user

    if os.environ.get("GEMINI_SKILLS_SIMPLE_INSTALLER") == "1":
        return manual_ask_user

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return manual_ask_user

    if os.environ.get("CI", "").lower() in {"1", "true", "yes"}:
        return manual_ask_user

    return terminal_ask_user


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
    ask_user_fn = get_cli_ask_user()
    installer = SkillInstaller(published_dir, ask_user_fn, logger)
    available = installer.get_available_skills()
    
    if not available:
        changed = installer.ensure_managed_gitignore_entries(target_project)
        logger.info("No skills found to install.")
        logger.info(
            "Managed .gitignore entries were %s.",
            "updated" if changed else "verified",
        )
        print("No skills found to install.")
        print(
            f"Managed .gitignore entries were {'updated' if changed else 'verified'}."
        )
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

    selector = SkillSelector(ask_user_fn)
    selected = selector.select_skills(available, installed_skills, updates)
    selected_skill_names = [os.path.basename(skill_path) for skill_path in selected]
    codex_candidates = [
        skill_name for skill_name in selected_skill_names if installer.supports_codex_bridge(skill_name)
    ]
    claude_candidates = [
        skill_name for skill_name in selected_skill_names if installer.supports_claude_reference(skill_name)
    ]
    install_codex_for = prompt_for_codex_support(ask_user_fn, codex_candidates)
    install_claude_for = prompt_for_claude_support(ask_user_fn, claude_candidates)

    for skill_path in selected:
        if installer.install_skill(skill_path, target_project):
            skill_name = os.path.basename(skill_path)
            if skill_name in install_codex_for:
                installer.install_codex_bridge(skill_name, target_project)
            if skill_name in install_claude_for:
                installer.install_claude_reference(skill_name, target_project)

    changed = installer.ensure_managed_gitignore_entries(target_project)
    if not selected:
        logger.info("No skills selected.")
        print("No skills selected.")
    logger.info(
        "Managed .gitignore entries were %s.",
        "updated" if changed else "verified",
    )
    print(
        f"Managed .gitignore entries were {'updated' if changed else 'verified'}."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        logging.getLogger("skill_installer").info("User closed the installer.")
        sys.exit(130)
