"""Interactive Gemini Skill Installer.
Allows users to install official skills from the 'published/' directory into their projects.
"""

import argparse
import os
import sys
import subprocess
import logging
import typing
import json
import shutil
import re
import time


KeyReader = typing.Callable[[], str]
AskUserResponse = typing.Dict[str, typing.Any]
ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_CYAN = "\x1b[36m"
ANSI_GREEN = "\x1b[32m"
ANSI_YELLOW = "\x1b[33m"
ANSI_WHITE = "\x1b[97m"
ANSI_GRAY = "\x1b[90m"
INSTALLER_BANNER = (
    " ____  _    _ _ _ _      __  __                                    \n"
    "/ ___|| | _(_) | | |    |  \\/  | __ _ _ __   __ _  __ _  ___ _ __  \n"
    "\\___ \\| |/ / | | | |____| |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__| \n"
    " ___) |   <| | | | |____| |  | | (_| | | | | (_| | (_| |  __/ |    \n"
    "|____/|_|\\_\\_|_|_|_|    |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|    \n"
    "                                                  |___/             "
)
GITIGNORE_MARKER_START = "# >>> skill-manager managed workspace files >>>"
GITIGNORE_MARKER_END = "# <<< skill-manager managed workspace files <<<"
MANAGED_SKILL_MANIFEST = ".gemini/skill-manager-manifest.json"
GITIGNORE_ENTRIES = [
    ".gemini/commands/",
    ".gemini/settings.json",
    MANAGED_SKILL_MANIFEST,
]
INSTALL_CONFIG_FILENAME = "install.config.json"


def supports_ansi(output_stream: typing.Optional[typing.TextIO] = None) -> bool:
    """Return whether ANSI color output should be used."""
    stream = output_stream or sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    if sys.platform != "win32":
        return True
    return os.environ.get("TERM_PROGRAM") is not None or "WT_SESSION" in os.environ


def style_text(
    text: str,
    *styles: str,
    enable_color: bool,
) -> str:
    """Apply ANSI styles only when color is enabled."""
    if not enable_color or not styles:
        return text
    return f"{''.join(styles)}{text}{ANSI_RESET}"


def installer_banner_text(
    enable_color: bool,
    subtitle: str = "Skill-Manager Installer",
) -> str:
    """Build the ASCII installer title."""
    title = style_text(INSTALLER_BANNER, ANSI_CYAN, ANSI_BOLD, enable_color=enable_color)
    subtitle = style_text(
        subtitle,
        ANSI_GREEN,
        ANSI_BOLD,
        enable_color=enable_color,
    )
    return f"{title}\n{subtitle}"


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
        updates: typing.Optional[typing.List[typing.Dict[str, str]]] = None,
        *,
        header: str = "Select Skills",
        question_text: str = "Which skills would you like to install or update?",
        banner_subtitle: str = "Skill-Manager Installer",
        close_label: str = "installer",
        description_formatter: typing.Optional[
            typing.Callable[[str, str, str], str]
        ] = None,
    ) -> typing.List[typing.List[str]]:
        """Prompt user and return only the selected labels."""
        selected, _action = self.select_skills_with_action(
            available_skills,
            installed_skills,
            updates,
            header=header,
            question_text=question_text,
            banner_subtitle=banner_subtitle,
            close_label=close_label,
            description_formatter=description_formatter,
        )
        return selected

    def select_skills_with_action(
        self,
        available_skills: typing.Dict[str, typing.List[str]],
        installed_skills: typing.Optional[typing.Dict[str, str]] = None,
        updates: typing.Optional[typing.List[typing.Dict[str, str]]] = None,
        *,
        header: str = "Select Skills",
        question_text: str = "Which skills would you like to install or update?",
        banner_subtitle: str = "Skill-Manager Installer",
        close_label: str = "installer",
        description_formatter: typing.Optional[
            typing.Callable[[str, str, str], str]
        ] = None,
        switch_action: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    ) -> typing.Tuple[typing.List[str], typing.Optional[str]]:
        """Prompt user to select skills from available categories with status info."""
        options: typing.List[typing.Dict[str, str]] = []
        installed = installed_skills or {}
        
        # Create a mapping of update name to its update info dictionary
        update_map = {u["name"]: u for u in (updates or [])}

        for category, skills in available_skills.items():
            for skill in skills:
                label = f"{category}/{skill}"
                status = ""
                state = "new"
                if skill in update_map:
                    update_info = update_map[skill]
                    status = (
                        " [Update Available] "
                        f"({update_info['installed']} -> {update_info['latest']})"
                    )
                    state = "update"
                elif skill in installed:
                    status = f" [Installed v{installed[skill]}]"
                    state = "installed"

                description = (
                    description_formatter(category, skill, status)
                    if description_formatter is not None
                    else f"Official {category} skill: {skill}{status}"
                )
                options.append({
                    "label": label,
                    "description": description,
                    "state": state,
                })

        if not options:
            return []

        response = self.ask_user({
            "questions": [{
                "header": header,
                "question": question_text,
                "banner_subtitle": banner_subtitle,
                "close_label": close_label,
                "switch_action": dict(switch_action or {}),
                "type": "choice",
                "multiSelect": True,
                "options": options
            }]
        })

        # Parse the standard tool response structure
        if isinstance(response, dict) and "answers" in response:
            return response["answers"]["0"], self._extract_action(response)
        
        return [], None

    @staticmethod
    def _extract_action(response: typing.Mapping[str, typing.Any]) -> typing.Optional[str]:
        action = response.get("action")
        if action is None:
            return None
        value = str(action).strip()
        return value or None


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
        self.enable_color = supports_ansi(self.output_stream)
        self.group_names, self.grouped_indices = self._build_groups()
        self.active_group = 0
        self.group_cursor_positions = [0 for _ in self.group_names]
        self.has_rendered = False
        self.last_rendered_line_count = 0

    def run(self, read_key: typing.Optional[KeyReader] = None) -> typing.List[str]:
        """Run the interactive selector and return selected labels."""
        labels, _action = self.run_with_action(read_key=read_key)
        return labels

    def run_with_action(
        self,
        read_key: typing.Optional[KeyReader] = None,
    ) -> typing.Tuple[typing.List[str], typing.Optional[str]]:
        """Run the interactive selector and return selected labels plus any UI action."""
        if not self.options:
            return [], None

        if read_key is None:
            read_key = self._create_key_reader()

        switch_action = self._normalized_switch_action()
        self._hide_cursor()
        try:
            while True:
                self._render()
                key = read_key()

                if key in {"\x03", "CTRL_C"}:
                    raise KeyboardInterrupt
                if key in {"UP", "k"}:
                    self._move_cursor(-1)
                    continue
                if key in {"DOWN", "j"}:
                    self._move_cursor(1)
                    continue
                if key in {"LEFT", "h"}:
                    self._move_group(-1)
                    continue
                if key in {"RIGHT", "l"}:
                    self._move_group(1)
                    continue
                if key == "SPACE":
                    current_index = self._current_option_index()
                    if self.multi_select:
                        if current_index in self.selected:
                            self.selected.remove(current_index)
                        else:
                            self.selected.add(current_index)
                    else:
                        self.selected = {current_index}
                    continue
                if key in {"ENTER", "\r", "\n"}:
                    if not self.multi_select:
                        self.selected = {self._current_option_index()}
                    break
                if key in {"a", "A"} and self.multi_select:
                    if len(self.selected) == len(self.options):
                        self.selected.clear()
                    else:
                        self.selected = set(range(len(self.options)))
                    continue
                if switch_action and key in switch_action["keys"]:
                    return [], switch_action["action"]
                if key in {"q", "Q", "ESC"}:
                    raise KeyboardInterrupt
        finally:
            self._clear_screen()
            self._show_cursor()

        return [self.options[index]["label"] for index in sorted(self.selected)], None

    def _render(self) -> None:
        self._prepare_screen()
        frame_lines = [
            *installer_banner_text(
                self.enable_color,
                self.question.get("banner_subtitle", "Skill-Manager Installer"),
            ).splitlines(),
            "",
        ]
        question = self.question.get("question", "Select option(s):")
        frame_lines.append(style_text(question, ANSI_BOLD, enable_color=self.enable_color))
        if self._has_multiple_groups():
            frame_lines.append(style_text("Categories", ANSI_BOLD, enable_color=self.enable_color))
            frame_lines.extend(self._format_tab_bar().splitlines())
            frame_lines.append(
                style_text(
                    self._format_tab_status_line(),
                    ANSI_CYAN,
                    enable_color=self.enable_color,
                )
            )
        if self.multi_select:
            frame_lines.extend(
                style_text(
                    (
                        "Use arrows to move, left/right to switch tabs, space to toggle, "
                        "A to select all, Enter to confirm."
                        if self._has_multiple_groups()
                        else "Use arrows, space to toggle, A to select all, Enter to confirm."
                    ),
                    ANSI_YELLOW,
                    enable_color=self.enable_color,
                )
                .splitlines()
            )
            switch_hint = self._switch_hint_text()
            if switch_hint:
                frame_lines.extend(
                    style_text(
                        switch_hint,
                        ANSI_CYAN,
                        enable_color=self.enable_color,
                    ).splitlines()
                )
            frame_lines.append("")
        else:
            frame_lines.extend(
                style_text(
                    (
                        "Use arrows to move, left/right to switch tabs, Enter to confirm."
                        if self._has_multiple_groups()
                        else "Use arrows and Enter to confirm."
                    ),
                    ANSI_YELLOW,
                    enable_color=self.enable_color,
                )
                .splitlines()
            )
            switch_hint = self._switch_hint_text()
            if switch_hint:
                frame_lines.extend(
                    style_text(
                        switch_hint,
                        ANSI_CYAN,
                        enable_color=self.enable_color,
                    ).splitlines()
                )
            frame_lines.append("")

        for index in self.grouped_indices[self.active_group]:
            option = self.options[index]
            state = str(option.get("state", "new"))
            pointer = (
                style_text(">", ANSI_GREEN, ANSI_BOLD, enable_color=self.enable_color)
                if index == self._current_option_index()
                else " "
            )
            selected = "[x]" if index in self.selected else "[ ]"
            if not self.multi_select:
                selected = "(*)" if index in self.selected else "( )"
            description = option.get("description", "")
            label_styles, description_styles = self._option_styles(state)
            frame_lines.extend(
                [
                    (
                        f"{pointer} {selected} "
                        f"{style_text(option['label'], *label_styles, enable_color=self.enable_color)}"
                    ),
                    (
                        "    "
                        f"{style_text(description, *description_styles, enable_color=self.enable_color)}"
                    ),
                ]
            )
        self._write_frame(frame_lines)

    def _clear_screen(self) -> None:
        self.output_stream.write("\x1b[2J\x1b[H")
        self.output_stream.flush()

    def _prepare_screen(self) -> None:
        if not self.has_rendered:
            self._clear_screen()
            self.has_rendered = True
            return
        self.output_stream.write("\x1b[H")
        self.output_stream.flush()

    def _write_frame(self, frame_lines: typing.Sequence[str]) -> None:
        visible_lines = len(frame_lines)
        padded_lines = list(frame_lines)
        if self.last_rendered_line_count > visible_lines:
            padded_lines.extend("" for _ in range(self.last_rendered_line_count - visible_lines))

        for line in padded_lines:
            self.output_stream.write(f"\x1b[2K{line}\n")
        self.output_stream.write("\x1b[H")
        self.output_stream.flush()
        self.last_rendered_line_count = visible_lines

    def _option_styles(self, state: str) -> typing.Tuple[typing.Tuple[str, ...], typing.Tuple[str, ...]]:
        if state == "installed":
            return ((ANSI_GRAY,), (ANSI_GRAY,))
        if state == "update":
            return ((ANSI_YELLOW, ANSI_BOLD), (ANSI_YELLOW,))
        return ((ANSI_WHITE, ANSI_BOLD), tuple())

    def _hide_cursor(self) -> None:
        self.output_stream.write("\x1b[?25l")
        self.output_stream.flush()

    def _show_cursor(self) -> None:
        self.output_stream.write("\x1b[?25h")
        self.output_stream.flush()

    def _normalized_switch_action(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        raw = self.question.get("switch_action")
        if not isinstance(raw, dict):
            return None

        key = str(raw.get("key", "")).strip()
        action = str(raw.get("action", "")).strip()
        if not key or not action:
            return None

        keys = {key, key.lower(), key.upper()}
        for extra in raw.get("keys", []):
            value = str(extra).strip()
            if value:
                keys.add(value)
        return {
            "key": key,
            "keys": keys,
            "action": action,
            "label": str(raw.get("label", "")).strip(),
        }

    def _switch_hint_text(self) -> str:
        switch_action = self._normalized_switch_action()
        if not switch_action:
            return ""
        label = switch_action["label"] or "go back"
        key = switch_action["key"]
        pretty_key = "Backspace" if key.upper() == "BACKSPACE" else key.upper()
        return f"Press {pretty_key} to {label}."

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
            if char == "\x08":
                return "BACKSPACE"
            if char == "\x1b":
                return "ESC"
            if char in {"\x00", "\xe0"}:
                special = msvcrt.getwch()
                return {
                    "H": "UP",
                    "P": "DOWN",
                    "K": "LEFT",
                    "M": "RIGHT",
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
                if char in {"\x08", "\x7f"}:
                    return "BACKSPACE"
                if char in {"\r", "\n"}:
                    return "ENTER"
                if char == " ":
                    return "SPACE"
                if char == "\x1b":
                    next_char = input_stream.read(1)
                    if next_char in {"[", "O"}:
                        arrow = input_stream.read(1)
                        return {
                            "A": "UP",
                            "B": "DOWN",
                            "C": "RIGHT",
                            "D": "LEFT",
                        }.get(arrow, "ESC")
                    return "ESC"
                return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return read_key

    def _build_groups(self) -> typing.Tuple[typing.List[str], typing.List[typing.List[int]]]:
        groups: typing.Dict[str, typing.List[int]] = {}
        order: typing.List[str] = []
        for index, option in enumerate(self.options):
            label = str(option.get("label", ""))
            category = label.split("/", 1)[0] if "/" in label else "All"
            if category not in groups:
                groups[category] = []
                order.append(category)
            groups[category].append(index)
        return order or ["All"], [groups[name] for name in order] or [list(range(len(self.options)))]

    def _has_multiple_groups(self) -> bool:
        return len(self.group_names) > 1

    def _format_tab_bar(self) -> str:
        tab_parts: typing.List[str] = []
        for group_index, group_name in enumerate(self.group_names):
            option_count = len(self.grouped_indices[group_index])
            if group_index == self.active_group:
                label = f"[ {group_name.upper()} | {option_count} ]"
                tab_parts.append(
                    style_text(label, ANSI_CYAN, ANSI_BOLD, enable_color=self.enable_color)
                )
            else:
                label = f"  {group_name} ({option_count})  "
                tab_parts.append(style_text(label, ANSI_YELLOW, enable_color=self.enable_color))
        width = max(36, sum(len(part) for part in tab_parts) + max(len(tab_parts) - 1, 0))
        separator = style_text("=" * width, ANSI_CYAN, enable_color=self.enable_color)
        return "\n".join([" ".join(tab_parts), separator])

    def _format_tab_status_line(self) -> str:
        active_name = self.group_names[self.active_group]
        active_count = len(self.grouped_indices[self.active_group])
        selected_in_group = sum(
            1 for index in self.grouped_indices[self.active_group] if index in self.selected
        )
        total_selected = len(self.selected)
        return (
            f"Active tab: {active_name} ({active_count})"
            f" | Selected here: {selected_in_group}"
            f" | Total selected: {total_selected}"
        )

    def _current_group_indices(self) -> typing.List[int]:
        return self.grouped_indices[self.active_group]

    def _current_option_index(self) -> int:
        return self._current_group_indices()[self.group_cursor_positions[self.active_group]]

    def _move_cursor(self, delta: int) -> None:
        indices = self._current_group_indices()
        if not indices:
            return
        group_cursor = self.group_cursor_positions[self.active_group]
        self.group_cursor_positions[self.active_group] = (group_cursor + delta) % len(indices)

    def _move_group(self, delta: int) -> None:
        if not self._has_multiple_groups():
            return
        self.active_group = (self.active_group + delta) % len(self.group_names)


class SkillInstaller:
    """Handle directory scanning and junction creation logic."""

    published_dir: str
    ask_user: typing.Callable
    logger: logging.Logger
    version_comparator: typing.Any
    install_config: typing.Dict[str, typing.Any]

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
        self.install_config = self._load_install_config()
        
        if version_comparator is None:
            from versioning import VersionComparator
            self.version_comparator = VersionComparator
        else:
            self.version_comparator = version_comparator

    def _load_install_config(self) -> typing.Dict[str, typing.Any]:
        """Load optional repo-level installer capabilities and distribution config."""
        config_path = os.path.join(os.path.dirname(self.published_dir), INSTALL_CONFIG_FILENAME)
        if not os.path.exists(config_path):
            return {"defaults": {"distribution": "shared", "supports": {}}, "skills": {}}

        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            self.logger.error("Error parsing install config at '%s': %s", config_path, exc)
            return {"defaults": {"distribution": "shared", "supports": {}}, "skills": {}}

        defaults = payload.get("defaults", {})
        skills = payload.get("skills", {})
        return {
            "defaults": {
                "distribution": defaults.get("distribution", "shared"),
                "supports": defaults.get("supports", {}),
            },
            "skills": skills if isinstance(skills, dict) else {},
        }

    def get_skill_config(self, skill_name: str) -> typing.Dict[str, typing.Any]:
        """Return the merged install config for a skill."""
        defaults = self.install_config.get("defaults", {})
        default_supports = defaults.get("supports", {})
        skill_config = self.install_config.get("skills", {}).get(skill_name, {})
        skill_supports = skill_config.get("supports", {})
        return {
            "distribution": skill_config.get("distribution", defaults.get("distribution", "shared")),
            "supports": {
                "codex_bridge": skill_supports.get(
                    "codex_bridge",
                    default_supports.get("codex_bridge", True),
                ),
                "claude_reference": skill_supports.get(
                    "claude_reference",
                    default_supports.get("claude_reference", True),
                ),
                "copilot_bridge": skill_supports.get(
                    "copilot_bridge",
                    default_supports.get("copilot_bridge", True),
                ),
            },
        }

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

    def _has_yaml_frontmatter(self, skill_md_path: str) -> bool:
        """Return whether a SKILL.md file starts with basic YAML frontmatter."""
        try:
            with open(skill_md_path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except OSError:
            return False

        stripped = content.lstrip()
        if not stripped.startswith("---"):
            return False

        lines = stripped.splitlines()
        if not lines or lines[0].strip() != "---":
            return False

        for line in lines[1:]:
            if line.strip() == "---":
                return True
        return False

    def codex_bridge_skill_content(self, skill_name: str, target_project_path: str) -> str:
        """Build a lightweight Codex bridge that points at the installed Gemini skill."""
        metadata = self.get_installed_skill_metadata(skill_name, target_project_path) or {}
        description = metadata.get(
            "description",
            (
                f"Codex bridge for the installed Gemini skill '{skill_name}'. "
                "Use the Gemini skill as the source of truth."
            ),
        )
        title = re.sub(r"[-_]+", " ", skill_name).strip().title() or skill_name
        return (
            "---\n"
            f"name: {skill_name}\n"
            f"description: {description}\n"
            "---\n\n"
            f"# {title} Bridge\n\n"
            f"Use the installed Gemini skill at `.gemini/skills/{skill_name}/SKILL.md` as the source of truth.\n\n"
            "Workflow:\n\n"
            f"1. Read and follow `.gemini/skills/{skill_name}/SKILL.md`.\n"
            "2. If that skill references scripts, metadata, or companion files, "
            f"resolve them from `.gemini/skills/{skill_name}/`.\n"
            "3. Do not duplicate the Gemini implementation in `.codex/skills/`. "
            "This bridge exists only so Codex can discover and invoke the "
            "installed Gemini skill guidance.\n\n"
            "## Codex Integration\n\n"
            "Use this bridge when Codex should apply the installed Gemini skill inside the current task.\n\n"
            "1. Treat the installed Gemini skill as the implementation source.\n"
            "2. Keep the Codex bridge lightweight and descriptive.\n"
            "3. If the project keeps `.codex/skills/` local-only, leave the "
            "generated bridge uncommitted and let `skill-manager` manage its "
            "ignore entry.\n"
        )

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
            "2. If that skill references scripts, metadata, or companion files, "
            f"resolve them from `.gemini/skills/{skill_name}/`.\n"
            "3. Do not duplicate the Gemini implementation in `.claude/skills/`. "
            "This reference exists only so Claude can discover and invoke the "
            "installed Gemini skill guidance.\n"
        )

    def copilot_bridge_skill_content(self, skill_name: str, target_project_path: str) -> str:
        """Build a lightweight Copilot CLI bridge that points at the installed Gemini skill."""
        metadata = self.get_installed_skill_metadata(skill_name, target_project_path) or {}
        description = metadata.get(
            "description",
            (
                f"Copilot CLI bridge for the installed Gemini skill '{skill_name}'. "
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
            "2. If that skill references scripts, metadata, or companion files, "
            f"resolve them from `.gemini/skills/{skill_name}/`.\n"
            "3. Do not duplicate the Gemini implementation in `.agents/skills/`. "
            "This reference exists only so Copilot CLI can discover and invoke the "
            "installed Gemini skill guidance.\n\n"
            "## Layer Conventions\n\n"
            "This project uses a four-layer skill structure:\n\n"
            "| Layer | Path | Consumer |\n"
            "|---|---|---|\n"
            "| Source of truth | `.gemini/skills/` | Gemini CLI |\n"
            "| Codex bridges | `.codex/skills/` | Codex / OpenAI agents |\n"
            "| Claude references | `.claude/skills/` | Claude Code |\n"
            "| Copilot bridges | `.agents/skills/` | Copilot CLI |\n\n"
            "When installing new skills, ensure all four layers are kept in sync for shared skills.\n"
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
            if (
                os.path.isdir(bridge_path)
                and not item.startswith(".")
                and os.path.isfile(skill_md)
                and self._has_yaml_frontmatter(skill_md)
            ):
                bridges.add(item)
        return bridges

    def supports_codex_bridge(self, skill_name: str) -> bool:
        """Check whether a skill can get a Codex bridge."""
        if not skill_name:
            return False
        skill_config = self.get_skill_config(skill_name)
        return bool(skill_config["supports"].get("codex_bridge", True))

    def supports_claude_reference(self, skill_name: str) -> bool:
        """Check whether a skill can get a generated Claude reference skill."""
        if not skill_name:
            return False
        skill_config = self.get_skill_config(skill_name)
        return bool(skill_config["supports"].get("claude_reference", True))

    def supports_copilot_bridge(self, skill_name: str) -> bool:
        """Check whether a skill can get a generated Copilot CLI bridge skill."""
        if not skill_name:
            return False
        skill_config = self.get_skill_config(skill_name)
        return bool(skill_config["supports"].get("copilot_bridge", True))

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
        manifest = self._normalize_managed_skill_manifest(
            target_project_path,
            self._load_managed_skill_manifest(target_project_path),
        )
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
            return {"gemini": [], "codex": [], "claude": [], "copilot": []}

        manifest: typing.Dict[str, typing.List[str]] = {}
        for key in ("gemini", "codex", "claude", "copilot"):
            values = payload.get(key, [])
            manifest[key] = sorted({str(value) for value in values if str(value).strip()})
        return manifest

    def _read_managed_gitignore_entries(
        self,
        target_project_path: str,
    ) -> typing.Dict[str, typing.List[str]]:
        """Recover managed skill entries from the existing skill-manager gitignore block."""
        gitignore_path = os.path.join(target_project_path, ".gitignore")
        manifest: typing.Dict[str, typing.List[str]] = {"gemini": [], "codex": [], "claude": [], "copilot": []}
        if not os.path.exists(gitignore_path):
            return manifest

        with open(gitignore_path, "r", encoding="utf-8") as handle:
            content = handle.read()

        if GITIGNORE_MARKER_START not in content or GITIGNORE_MARKER_END not in content:
            return manifest

        start = content.index(GITIGNORE_MARKER_START) + len(GITIGNORE_MARKER_START)
        end = content.index(GITIGNORE_MARKER_END)
        block = content[start:end]
        prefixes = {
            "gemini": ".gemini/skills/",
            "codex": ".codex/skills/",
            "claude": ".claude/skills/",
            "copilot": ".agents/skills/",
        }

        for raw_line in block.splitlines():
            line = raw_line.strip()
            for kind, prefix in prefixes.items():
                if line.startswith(prefix) and line.endswith("/"):
                    skill_name = line[len(prefix):-1].strip()
                    if skill_name:
                        manifest[kind].append(skill_name)
                    break

        for kind in manifest:
            manifest[kind] = sorted(set(manifest[kind]))
        return manifest

    def _discover_managed_skills(
        self,
        target_project_path: str,
    ) -> typing.Dict[str, typing.List[str]]:
        """Bootstrap managed skills from the existing skill-manager gitignore block."""
        return self._read_managed_gitignore_entries(target_project_path)

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

    def _companion_skill_still_supported(self, kind: str, skill_name: str) -> bool:
        """Return whether a managed companion skill is still eligible under install config."""
        if kind == "codex":
            return self.supports_codex_bridge(skill_name)
        if kind == "claude":
            return self.supports_claude_reference(skill_name)
        if kind == "copilot":
            return self.supports_copilot_bridge(skill_name)
        return True

    def _normalize_managed_skill_manifest(
        self,
        target_project_path: str,
        manifest: typing.Dict[str, typing.List[str]],
    ) -> typing.Dict[str, typing.List[str]]:
        """Prune stale managed companion artifacts that are no longer supported."""
        base_paths = {
            "gemini": os.path.join(target_project_path, ".gemini", "skills"),
            "codex": os.path.join(target_project_path, ".codex", "skills"),
            "claude": os.path.join(target_project_path, ".claude", "skills"),
            "copilot": os.path.join(target_project_path, ".agents", "skills"),
        }
        normalized: typing.Dict[str, typing.List[str]] = {}
        changed = False

        for kind in ("gemini", "codex", "claude", "copilot"):
            kept: typing.List[str] = []
            for skill_name in manifest.get(kind, []):
                skill_path = os.path.join(base_paths[kind], skill_name)
                if kind in ("codex", "claude", "copilot") and not self._companion_skill_still_supported(kind, skill_name):
                    if os.path.isdir(skill_path):
                        self._remove_directory_tree(skill_path)
                    changed = True
                    continue
                if not os.path.isdir(skill_path):
                    changed = True
                    continue
                kept.append(skill_name)
            normalized[kind] = sorted(set(kept))
            if normalized[kind] != sorted(set(manifest.get(kind, []))):
                changed = True

        if changed:
            self._write_managed_skill_manifest(target_project_path, normalized)
        return normalized

    def _register_managed_skill(
        self,
        target_project_path: str,
        kind: str,
        skill_name: str,
    ) -> None:
        """Record a skill directory as being installed by skill-manager."""
        manifest = self._normalize_managed_skill_manifest(
            target_project_path,
            self._load_managed_skill_manifest(target_project_path),
        )
        current = set(manifest.get(kind, []))
        current.add(skill_name)
        manifest[kind] = sorted(current)
        self._write_managed_skill_manifest(target_project_path, manifest)

    def _unregister_managed_skill(
        self,
        target_project_path: str,
        kind: str,
        skill_name: str,
    ) -> None:
        """Remove a skill directory from the managed manifest."""
        manifest = self._normalize_managed_skill_manifest(
            target_project_path,
            self._load_managed_skill_manifest(target_project_path),
        )
        current = set(manifest.get(kind, []))
        if skill_name in current:
            current.remove(skill_name)
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
            "copilot": ".agents/skills",
        }
        for kind in ("gemini", "codex", "claude", "copilot"):
            base_path = base_paths[kind]
            for skill_name in manifest.get(kind, []):
                entries.append(f"{base_path}/{skill_name}/")
        return entries

    def get_managed_skill_names(self, target_project_path: str) -> typing.List[str]:
        """Return the set of skill names currently managed by skill-manager."""
        manifest = self._normalize_managed_skill_manifest(
            target_project_path,
            self._load_managed_skill_manifest(target_project_path),
        )
        names = set()
        for kind in ("gemini", "codex", "claude", "copilot"):
            names.update(manifest.get(kind, []))
        return sorted(names)

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
        """Install a lightweight Codex bridge wrapper for a skill."""
        source_skill_path = os.path.join(
            target_project_path,
            ".gemini",
            "skills",
            skill_name,
            "SKILL.md",
        )
        if not os.path.isfile(source_skill_path):
            self.logger.info(
                f"Skipping Codex bridge for '{skill_name}': the Gemini skill is not installed in the target project."
            )
            return False

        if not self.supports_codex_bridge(skill_name):
            self.logger.info(
                f"Skipping Codex bridge for '{skill_name}': this skill is not eligible for Codex bridge generation."
            )
            return False

        source_path = os.path.join(self.codex_bridges_dir(), skill_name)
        target_skills_dir = os.path.join(target_project_path, ".codex", "skills")
        os.makedirs(target_skills_dir, exist_ok=True)
        target_path = os.path.join(target_skills_dir, skill_name)
        target_skill_path = os.path.join(target_path, "SKILL.md")

        self.logger.info(f"Installing Codex bridge for '{skill_name}'...")
        try:
            source_wrapper_path = os.path.join(source_path, "SKILL.md")
            if os.path.isfile(source_wrapper_path) and self._has_yaml_frontmatter(source_wrapper_path):
                abs_source = os.path.abspath(source_path)
                abs_target = os.path.abspath(target_path)
                if os.path.normcase(abs_source) != os.path.normcase(abs_target):
                    self._copy_skill_files(abs_source, abs_target)
            else:
                if os.path.isfile(source_wrapper_path):
                    self.logger.warning(
                        "Skipping invalid repo-owned Codex bridge for '%s' at '%s'; "
                        "falling back to generated bridge content.",
                        skill_name,
                        source_wrapper_path,
                    )
                os.makedirs(target_path, exist_ok=True)
                content = self.codex_bridge_skill_content(skill_name, target_project_path)
                with open(target_skill_path, "w", encoding="utf-8") as handle:
                    handle.write(content)
            self._register_managed_skill(target_project_path, "codex", skill_name)
            self.ensure_managed_gitignore_entries(target_project_path)
            self.logger.info(f"Successfully installed Codex bridge for '{skill_name}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to install Codex bridge for '{skill_name}': {e}")
            return False

    def install_claude_reference(self, skill_name: str, target_project_path: str) -> bool:
        """Install a lightweight Claude reference skill for an installed Gemini skill."""
        source_skill_path = os.path.join(
            target_project_path,
            ".gemini",
            "skills",
            skill_name,
            "SKILL.md",
        )
        if not os.path.isfile(source_skill_path):
            self.logger.info(
                "Skipping Claude reference for '%s': the Gemini skill is not "
                "installed in the target project.",
                skill_name,
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

    def install_copilot_bridge(self, skill_name: str, target_project_path: str) -> bool:
        """Install a lightweight Copilot CLI bridge skill for an installed Gemini skill."""
        source_skill_path = os.path.join(
            target_project_path,
            ".gemini",
            "skills",
            skill_name,
            "SKILL.md",
        )
        if not os.path.isfile(source_skill_path):
            self.logger.info(
                "Skipping Copilot bridge for '%s': the Gemini skill is not "
                "installed in the target project.",
                skill_name,
            )
            return False

        if not self.supports_copilot_bridge(skill_name):
            self.logger.info(
                f"Skipping Copilot bridge for '{skill_name}': this skill is not eligible for Copilot bridge generation."
            )
            return False

        target_skill_dir = os.path.join(target_project_path, ".agents", "skills", skill_name)
        os.makedirs(target_skill_dir, exist_ok=True)
        target_skill_path = os.path.join(target_skill_dir, "SKILL.md")

        self.logger.info(f"Installing Copilot CLI bridge for '{skill_name}'...")
        try:
            content = self.copilot_bridge_skill_content(skill_name, target_project_path)
            with open(target_skill_path, "w", encoding="utf-8") as handle:
                handle.write(content)
            self._register_managed_skill(target_project_path, "copilot", skill_name)
            self.ensure_managed_gitignore_entries(target_project_path)
            self.logger.info(f"Successfully installed Copilot CLI bridge for '{skill_name}'.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to install Copilot CLI bridge for '{skill_name}': {e}")
            return False

    def uninstall_skill(self, skill_name: str, target_project_path: str) -> bool:
        """Remove a managed Gemini skill and any managed Codex/Claude/Copilot companions."""
        if not skill_name:
            return False

        if skill_name not in self.get_managed_skill_names(target_project_path):
            return False

        removed = False
        targets = {
            "gemini": os.path.join(target_project_path, ".gemini", "skills", skill_name),
            "codex": os.path.join(target_project_path, ".codex", "skills", skill_name),
            "claude": os.path.join(target_project_path, ".claude", "skills", skill_name),
            "copilot": os.path.join(target_project_path, ".agents", "skills", skill_name),
        }

        failed_kinds: typing.Set[str] = set()
        for kind, path in targets.items():
            if os.path.isdir(path):
                try:
                    self._remove_directory_tree(path)
                    removed = True
                except OSError as exc:
                    failed_kinds.add(kind)
                    self.logger.error(
                        "Failed to uninstall '%s' %s artifact at '%s': %s",
                        skill_name,
                        kind,
                        path,
                        exc,
                    )
                    continue
            if kind not in failed_kinds:
                self._unregister_managed_skill(target_project_path, kind, skill_name)

        self.ensure_managed_gitignore_entries(target_project_path)
        return removed and not failed_kinds

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

    def _remove_directory_tree(self, path: str) -> None:
        """Remove a directory tree or legacy link/junction safely."""
        if self._is_link_or_junction(path):
            self._remove_junction(path)
            return
        attempts = 5 if sys.platform == "win32" else 1
        delay_seconds = 0.2
        last_error: typing.Optional[OSError] = None

        for attempt in range(attempts):
            try:
                shutil.rmtree(path)
                return
            except PermissionError as exc:
                last_error = exc
                if sys.platform != "win32" or attempt == attempts - 1:
                    raise
                time.sleep(delay_seconds)

        if last_error is not None:
            raise last_error

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
    enable_color = supports_ansi(sys.stdout)

    print(installer_banner_text(enable_color, question.get("banner_subtitle", "Skill-Manager Installer")))
    print()
    print(style_text(question["question"], ANSI_BOLD, enable_color=enable_color))
    if is_multi:
        print(
            style_text(
                "(Select multiple with spaces or commas, ranges like 1-3, or 'all')",
                ANSI_YELLOW,
                enable_color=enable_color,
            )
        )
    switch_action = question.get("switch_action")
    if isinstance(switch_action, dict):
        switch_key = str(switch_action.get("key", "")).strip()
        switch_label = str(switch_action.get("label", "")).strip()
        if switch_key and switch_label:
            pretty_key = "Backspace" if switch_key.upper() == "BACKSPACE" else switch_key
            print(
                style_text(
                    f"(Type '{pretty_key}' to {switch_label})",
                    ANSI_CYAN,
                    enable_color=enable_color,
                )
            )
    for i, opt in enumerate(question['options']):
        print(
            f"{style_text(str(i + 1), ANSI_GREEN, ANSI_BOLD, enable_color=enable_color)}: "
            f"{style_text(opt['label'], ANSI_BOLD, enable_color=enable_color)} - {opt['description']}"
        )
    
    try:
        selection = input("\nEnter choice(s): ")
    except KeyboardInterrupt:
        print(f"\nUser closed the {question.get('close_label', 'installer')}.")
        raise

    switch_response = _manual_switch_response(question, selection)
    if switch_response is not None:
        return switch_response

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
    labels, action = selector.run_with_action()
    if question.get("type") == "choice" and not question.get("multiSelect", False):
        answer: typing.Any = labels[0] if labels else ""
    else:
        answer = labels
    response: typing.Dict[str, typing.Any] = {"answers": {"0": answer}}
    if action:
        response["action"] = action
    return response


def _manual_switch_response(
    question: typing.Mapping[str, typing.Any],
    raw_selection: str,
) -> typing.Optional[typing.Dict[str, typing.Any]]:
    switch_action = question.get("switch_action")
    if not isinstance(switch_action, dict):
        return None

    action = str(switch_action.get("action", "")).strip()
    value = raw_selection.strip().lower()
    if not action or not value:
        return None

    aliases = {
        str(alias).strip().lower()
        for alias in switch_action.get("aliases", [])
        if str(alias).strip()
    }
    key = str(switch_action.get("key", "")).strip().lower()
    if value not in ({key} | aliases):
        return None

    return {"answers": {"0": []}, "action": action}


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


def prompt_for_copilot_support(
    ask_user_fn: typing.Callable[[typing.Dict[str, typing.Any]], AskUserResponse],
    skill_names: typing.Sequence[str],
) -> typing.Set[str]:
    """Ask whether selected skills should also receive Copilot CLI bridge skills."""
    bridgeable = sorted(set(skill_names))
    if not bridgeable:
        return set()

    response = ask_user_fn({
        "questions": [{
            "header": "Copilot CLI Support",
            "question": (
                "Install generated Copilot CLI bridge skills in .agents/skills for the selected skills?"
            ),
            "type": "choice",
            "multiSelect": False,
            "options": [
                {
                    "label": "yes",
                    "description": "Add lightweight Copilot CLI bridge skills that point at the installed Gemini skills.",
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


def find_git_root(start_path: str) -> typing.Optional[str]:
    """Return the nearest parent directory that contains a .git entry."""
    current = os.path.abspath(start_path)

    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current

        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def resolve_target_project_path(argv: typing.Optional[typing.Sequence[str]] = None) -> str:
    """Resolve the project path the installer should mutate."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--target-project",
        "--project-root",
        dest="target_project",
    )
    parsed, _unknown = parser.parse_known_args(list(argv or sys.argv[1:]))
    if parsed.target_project:
        return os.path.abspath(parsed.target_project)

    current_dir = os.getcwd()
    git_root = find_git_root(current_dir)
    if git_root:
        return os.path.abspath(git_root)
    return os.path.abspath(current_dir)


def print_target_project_summary(
    target_project: str,
    *,
    skill_names: typing.Optional[typing.Sequence[str]] = None,
    include_codex: bool = False,
    include_claude: bool = False,
    include_copilot: bool = False,
) -> None:
    """Show the exact project path and managed locations touched by the installer."""
    print(f"Target project: {target_project}")
    print(f"Gemini skills: {os.path.join(target_project, '.gemini', 'skills')}")
    if include_codex:
        print(f"Codex bridges: {os.path.join(target_project, '.codex', 'skills')}")
    if include_claude:
        print(f"Claude references: {os.path.join(target_project, '.claude', 'skills')}")
    if include_copilot:
        print(f"Copilot bridges: {os.path.join(target_project, '.agents', 'skills')}")
    if skill_names and "skill-manager" in set(skill_names):
        print(f"Gemini commands: {os.path.join(target_project, '.gemini', 'commands', 'skill-manager')}")
        print(f"Gemini settings: {os.path.join(target_project, '.gemini', 'settings.json')}")
        print(f"Managed manifest: {os.path.join(target_project, '.gemini', 'skill-manager-manifest.json')}")
        print(f"Gitignore: {os.path.join(target_project, '.gitignore')}")


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
    
    target_project = resolve_target_project_path()
    if not os.access(target_project, os.W_OK):
        logger.error(f"Target project directory is not writable: {target_project}")
        sys.exit(1)
    logger.info("Target project directory: %s", target_project)
    if os.path.abspath(target_project) == os.path.abspath(script_dir):
        logger.warning(
            "Installer target matches the gemini-skills repository root. "
            "Run the command from the destination repo root or pass --target-project <path> "
            "to install into a different project."
        )

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
    selected, action = selector.select_skills_with_action(
        available,
        installed_skills,
        updates,
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
    selected_skill_names = [os.path.basename(skill_path) for skill_path in selected]
    codex_candidates = [
        skill_name for skill_name in selected_skill_names if installer.supports_codex_bridge(skill_name)
    ]
    claude_candidates = [
        skill_name for skill_name in selected_skill_names if installer.supports_claude_reference(skill_name)
    ]
    copilot_candidates = [
        skill_name for skill_name in selected_skill_names if installer.supports_copilot_bridge(skill_name)
    ]
    install_codex_for = prompt_for_codex_support(ask_user_fn, codex_candidates)
    install_claude_for = prompt_for_claude_support(ask_user_fn, claude_candidates)
    install_copilot_for = prompt_for_copilot_support(ask_user_fn, copilot_candidates)

    for skill_path in selected:
        if installer.install_skill(skill_path, target_project):
            skill_name = os.path.basename(skill_path)
            if skill_name in install_codex_for:
                installer.install_codex_bridge(skill_name, target_project)
            if skill_name in install_claude_for:
                installer.install_claude_reference(skill_name, target_project)
            if skill_name in install_copilot_for:
                installer.install_copilot_bridge(skill_name, target_project)

    changed = installer.ensure_managed_gitignore_entries(target_project)
    if not selected:
        logger.info("No skills selected.")
        print("No skills selected.")
    else:
        print_target_project_summary(
            target_project,
            skill_names=selected_skill_names,
            include_codex=bool(install_codex_for),
            include_claude=bool(install_claude_for),
            include_copilot=bool(install_copilot_for),
        )
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
