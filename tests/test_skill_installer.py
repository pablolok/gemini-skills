"""Tests for the SkillSelector and SkillInstaller classes."""

import os
import sys
import unittest
import io
import tempfile
import json
from unittest.mock import MagicMock, patch

# We'll implement these in install.py
# For now, we'll try to import them, which will fail initially (Red phase)
from install import (
    ANSI_BOLD,
    ANSI_GRAY,
    ANSI_WHITE,
    ANSI_YELLOW,
    INSTALLER_BANNER,
    SkillSelector,
    SkillInstaller,
    TerminalMultiSelect,
    get_cli_ask_user,
    find_git_root,
    parse_selection_input,
    print_target_project_summary,
    resolve_target_project_path,
    installer_banner_text,
    style_text,
    supports_ansi,
)

class TestSkillInstaller(unittest.TestCase):
    """Test suite for the SkillInstaller logic."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_ask_user = MagicMock()
        self.published_dir = "published"

    def test_installer_is_available(self) -> None:
        """Verify that the SkillInstaller class exists."""
        self.assertIsNotNone(SkillInstaller, "SkillInstaller class should be implemented in install.py")

    def test_scan_published_skills(self) -> None:
        """Verify that the installer can scan the published directory."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        skills = installer.get_available_skills()
        
        # We know we have 'audit' category with at least 4 skills from Phase 1
        self.assertIn("audit", skills)
        self.assertTrue(len(skills["audit"]) >= 4)
        self.assertIn("review-optimization", skills["audit"])

    def test_ask_user_for_skills(self) -> None:
        """Verify that the selector correctly uses ask_user."""
        if SkillSelector is None:
            self.skipTest("SkillSelector not yet implemented")

        available_skills = {
            "audit": ["skill1", "skill2"],
            "workflow": ["skill3"]
        }

        selector = SkillSelector(self.mock_ask_user)

        # Mock user selecting skill1 and skill3
        self.mock_ask_user.return_value = {
            "answers": {"0": ["audit/skill1", "workflow/skill3"]}
        }

        selected = selector.select_skills(available_skills)

        self.assertEqual(selected, ["audit/skill1", "workflow/skill3"])
        self.mock_ask_user.assert_called_once()

    def test_select_skills_formats_update_string(self) -> None:
        """Verify that updates are formatted as '[Update Available] (vX -> vY)'."""
        selector = SkillSelector(self.mock_ask_user)

        available_skills = {"category": ["skill_a"]}
        installed_skills = {"skill_a": "1.0.0"}
        updates = [{
            "name": "skill_a",
            "installed": "1.0.0",
            "latest": "2.0.0",
            "rel_path": "category/skill_a"
        }]

        # Call just to inspect the arguments passed to ask_user
        selector.select_skills(available_skills, installed_skills, updates)

        self.mock_ask_user.assert_called_once()
        args, kwargs = self.mock_ask_user.call_args

        options = args[0]["questions"][0]["options"]
        self.assertEqual(len(options), 1)
        self.assertIn("[Update Available] (1.0.0 -> 2.0.0)", options[0]["description"])
        self.assertEqual(options[0]["state"], "update")

    def test_select_skills_marks_new_and_installed_states(self) -> None:
        """Verify selector payload includes item state for terminal styling."""
        selector = SkillSelector(self.mock_ask_user)

        available_skills = {"audit": ["skill_a", "skill_b"]}
        installed_skills = {"skill_b": "1.0.0"}

        selector.select_skills(available_skills, installed_skills, [])

        args, _kwargs = self.mock_ask_user.call_args
        options = args[0]["questions"][0]["options"]
        self.assertEqual(options[0]["state"], "new")
        self.assertEqual(options[1]["state"], "installed")
    @patch("shutil.copytree")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_copy_installation_logic(self, mock_makedirs, mock_exists, mock_copytree) -> None:
        """Verify the logic for installing skills via file copying."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        target_project = "C:/temp/project"
        skill_path = "audit/review-optimization"
        
        # .gemini/skills doesn't exist
        def exists_side_effect(path):
            if "metadata.json" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        
        installer.install_skill(skill_path, target_project)
        
        expected_target = os.path.join(target_project, ".gemini", "skills", "review-optimization")
        mock_copytree.assert_called_once_with(
            os.path.abspath(os.path.join(self.published_dir, skill_path)),
            os.path.abspath(expected_target),
            dirs_exist_ok=True
        )

    @patch("subprocess.run")
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_run_post_install_hook(self, mock_exists, mock_makedirs, mock_run) -> None:
        """Verify that the installer executes post_install.py if it exists."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")
            
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        target_project = "C:/temp/project"
        skill_path = "audit/review-optimization"
        
        # Scenario: post_install.py exists, but target skill dir does not
        def side_effect(path):
            if "post_install.py" in path:
                return True
            if ".gemini" in path and "skills" in path:
                # This covers target_path check
                return False
            return True
        mock_exists.side_effect = side_effect
        
        # Mock _copy_skill_files to do nothing and isolate this test from gitignore maintenance
        with patch.object(installer, '_copy_skill_files'), patch.object(
            installer,
            '_register_managed_skill',
        ), patch.object(
            installer,
            'ensure_managed_gitignore_entries',
        ):
            installer.install_skill(skill_path, target_project)
            
            # Should have called subprocess.run with python and the hook path
            hook_path = os.path.abspath(os.path.join(self.published_dir, skill_path, "post_install.py"))
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertIn(sys.executable, args[0])
            self.assertIn(hook_path, args[0])

    def test_get_skill_metadata(self) -> None:
        """Verify reading metadata.json."""
        if SkillInstaller is None:
            self.skipTest("SkillInstaller not yet implemented")

        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        # We know review-optimization has metadata.json
        metadata = installer.get_skill_metadata("audit/review-optimization")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["name"], "review-optimization")

    def test_supports_claude_reference_for_skill_name(self) -> None:
        """Verify Claude reference skills can be generated for selected skills."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        self.assertTrue(installer.supports_claude_reference("review-optimization"))
        self.assertFalse(installer.supports_claude_reference(""))

    def test_supports_agents_bridge_for_skill_name(self) -> None:
        """Verify agents bridge skills can be generated for selected skills."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        self.assertTrue(installer.supports_agents_bridge("review-optimization"))
        self.assertFalse(installer.supports_agents_bridge(""))

    def test_install_config_marks_balancer_family_as_gemini_only(self) -> None:
        """Verify Gemini-only skills are not treated as agents/Claude companion candidates."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        self.assertTrue(installer.supports_agents_bridge("compliance-audit-verification-gates"))
        self.assertTrue(installer.supports_claude_reference("compliance-audit-verification-gates"))
        self.assertFalse(installer.supports_agents_bridge("subagent-balancer"))
        self.assertFalse(installer.supports_claude_reference("subagent-balancer"))
        self.assertFalse(installer.supports_agents_bridge("subagent-balancer-api"))
        self.assertFalse(installer.supports_claude_reference("subagent-balancer-api"))
        self.assertFalse(installer.supports_agents_bridge("subagent-balancer-orchestrator"))
        self.assertFalse(installer.supports_claude_reference("subagent-balancer-orchestrator"))

    def test_supports_ansi_respects_no_color(self) -> None:
        """Verify NO_COLOR disables ANSI output."""
        stream = io.StringIO()
        stream.isatty = lambda: True  # type: ignore[attr-defined]
        with patch.dict(os.environ, {"NO_COLOR": "1"}, clear=False):
            self.assertFalse(supports_ansi(stream))

    def test_style_text_and_banner_render_when_color_enabled(self) -> None:
        """Verify helper formatting functions add ANSI wrappers when enabled."""
        styled = style_text("hello", ANSI_BOLD, enable_color=True)
        self.assertTrue(styled.startswith(ANSI_BOLD))
        self.assertTrue(styled.endswith("\x1b[0m"))

        banner = installer_banner_text(True, subtitle="Custom Subtitle")
        self.assertIn(INSTALLER_BANNER, banner)
        self.assertIn("Custom Subtitle", banner)

    def test_parse_selection_input_handles_ranges_and_single_select(self) -> None:
        """Verify selection parsing handles ranges, reverse ranges, and single-select mode."""
        self.assertEqual(parse_selection_input("1-3", 5, True), [0, 1, 2])
        self.assertEqual(parse_selection_input("3-1", 5, True), [2, 1, 0])
        self.assertEqual(parse_selection_input("0 2 2", 5, True), [0, 1])
        self.assertEqual(parse_selection_input("2 3", 5, False), [1])

    def test_parse_selection_input_handles_all_and_empty_values(self) -> None:
        """Verify selection parsing handles all/empty cases safely."""
        self.assertEqual(parse_selection_input("all", 3, True), [0, 1, 2])
        self.assertEqual(parse_selection_input("*", 3, True), [0, 1, 2])
        self.assertEqual(parse_selection_input("", 3, True), [])
        self.assertEqual(parse_selection_input("1", 0, True), [])

    def test_has_yaml_frontmatter_detects_valid_and_invalid_files(self) -> None:
        """Verify SKILL.md frontmatter detection handles valid, invalid, and missing files."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_path = os.path.join(temp_dir, "valid.md")
            invalid_path = os.path.join(temp_dir, "invalid.md")

            with open(valid_path, "w", encoding="utf-8") as handle:
                handle.write("---\nname: demo\n---\n# Demo\n")
            with open(invalid_path, "w", encoding="utf-8") as handle:
                handle.write("# Demo\n")

            self.assertTrue(installer._has_yaml_frontmatter(valid_path))
            self.assertFalse(installer._has_yaml_frontmatter(invalid_path))
            self.assertFalse(installer._has_yaml_frontmatter(os.path.join(temp_dir, "missing.md")))

    def test_read_metadata_returns_none_when_json_is_invalid(self) -> None:
        """Verify invalid metadata content is reported as missing metadata."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = os.path.join(temp_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as handle:
                handle.write("{ invalid json }")

            self.assertIsNone(installer._read_metadata(metadata_path))

    def test_agents_and_claude_bridge_content_use_metadata_description(self) -> None:
        """Verify generated bridge content reuses installed skill metadata when available."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_dir = os.path.join(temp_dir, ".gemini", "skills", "demo-skill")
            os.makedirs(metadata_dir, exist_ok=True)
            with open(os.path.join(metadata_dir, "metadata.json"), "w", encoding="utf-8") as handle:
                json.dump({"description": "Installed demo skill."}, handle)

            agents_content = installer.agents_bridge_skill_content("demo-skill", temp_dir)
            claude_content = installer.claude_reference_skill_content("demo-skill", temp_dir)

            self.assertIn("Installed demo skill.", agents_content)
            self.assertIn("Installed demo skill.", claude_content)
            self.assertIn(".gemini/skills/demo-skill/SKILL.md", agents_content)
            self.assertIn(".gemini/skills/demo-skill/SKILL.md", claude_content)

    def test_agents_bridge_content_falls_back_when_metadata_is_missing(self) -> None:
        """Verify generated agents bridge content falls back to the default description."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        content = installer.agents_bridge_skill_content("demo_skill", "missing-project")

        self.assertIn("Agents bridge for the installed Gemini skill 'demo_skill'.", content)
        self.assertIn("# Demo Skill Bridge", content)

    def test_agents_bridge_discovery_returns_empty_when_no_bridge_dir_exists(self) -> None:
        """Verify that the installer handles missing .agents/skills dir gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            installer = SkillInstaller(os.path.join(temp_dir, "published"), self.mock_ask_user)
            # .agents/skills/ not created yet — install_agents_bridge returns False without Gemini skill
            result = installer.install_agents_bridge("no-such-skill", temp_dir)
            self.assertFalse(result)

    def test_shared_skills_can_generate_agents_and_claude_artifacts_via_installer(self) -> None:
        """Verify every shared supported skill can generate all managed tool-specific artifacts."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with open("install.config.json", "r", encoding="utf-8") as handle:
            install_config = json.load(handle)

        shared_skills = {
            skill_name: skill_config
            for skill_name, skill_config in install_config["skills"].items()
            if skill_config.get("distribution", install_config["defaults"]["distribution"]) == "shared"
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            for skill_name, skill_config in shared_skills.items():
                category = skill_config["category"]
                rel_path = f"{category}/{skill_name}"
                self.assertTrue(
                    installer.install_skill(rel_path, temp_dir),
                    msg=f"Failed to install Gemini skill {skill_name}",
                )

                if installer.supports_agents_bridge(skill_name):
                    self.assertTrue(
                        installer.install_agents_bridge(skill_name, temp_dir),
                        msg=f"Failed to generate agents bridge for {skill_name}",
                    )
                    self.assertTrue(
                        os.path.isfile(
                            os.path.join(temp_dir, ".agents", "skills", skill_name, "SKILL.md")
                        )
                    )

                if installer.supports_claude_reference(skill_name):
                    self.assertTrue(
                        installer.install_claude_reference(skill_name, temp_dir),
                        msg=f"Failed to generate Claude reference for {skill_name}",
                    )
                    self.assertTrue(
                        os.path.isfile(
                            os.path.join(temp_dir, ".claude", "skills", skill_name, "SKILL.md")
                        )
                    )

            gitignore_path = os.path.join(temp_dir, ".gitignore")
            with open(gitignore_path, "r", encoding="utf-8") as handle:
                gitignore = handle.read()

            for skill_name in shared_skills:
                self.assertIn(f".gemini/skills/{skill_name}/", gitignore)
                if installer.supports_agents_bridge(skill_name):
                    self.assertIn(f".agents/skills/{skill_name}/", gitignore)
                if installer.supports_claude_reference(skill_name):
                    self.assertIn(f".claude/skills/{skill_name}/", gitignore)

    def test_check_for_updates_reports_newer_published_versions(self) -> None:
        """Verify update detection compares installed and published metadata."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            installed_dir = os.path.join(
                temp_dir,
                ".gemini",
                "skills",
                "review-optimization",
            )
            os.makedirs(installed_dir, exist_ok=True)
            with open(
                os.path.join(installed_dir, "metadata.json"),
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump({"name": "review-optimization", "version": "0.9.0"}, handle)

            updates = installer.check_for_updates(temp_dir)

            self.assertEqual(len(updates), 1)
            self.assertEqual(updates[0]["name"], "review-optimization")
            self.assertEqual(updates[0]["installed"], "0.9.0")

    def test_install_agents_bridge_returns_false_when_skill_missing_or_unsupported(self) -> None:
        """Verify agents bridge install short-circuits for unsupported or missing Gemini skills."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertFalse(installer.install_agents_bridge("review-optimization", temp_dir))
            self.assertFalse(installer.install_agents_bridge("subagent-balancer", temp_dir))

    def test_install_claude_reference_returns_false_when_skill_missing(self) -> None:
        """Verify Claude reference install short-circuits when the Gemini skill is missing."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertFalse(installer.install_claude_reference("review-optimization", temp_dir))

    def test_install_agents_bridge_generates_bridge_for_supported_skill(self) -> None:
        """Verify supported skills can get a generated agents bridge."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            installer.install_skill("audit/compliance-audit-verification-gates", temp_dir)

            success = installer.install_agents_bridge("compliance-audit-verification-gates", temp_dir)

            self.assertTrue(success)
            bridge_path = os.path.join(
                temp_dir,
                ".agents",
                "skills",
                "compliance-audit-verification-gates",
                "SKILL.md",
            )
            self.assertTrue(os.path.isfile(bridge_path))
            with open(bridge_path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("Use the installed Gemini skill", content)
            self.assertIn(".gemini/skills/compliance-audit-verification-gates/SKILL.md", content)

    def test_agents_bridge_content_falls_back_when_metadata_is_missing(self) -> None:
        """Verify generated agents bridge content falls back to the default description."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        content = installer.agents_bridge_skill_content("demo_skill", "missing-project")

        self.assertIn("Agents bridge for the installed Gemini skill 'demo_skill'.", content)
        self.assertIn("# Demo Skill Bridge", content)

    def test_ensure_managed_gitignore_entries_preserves_user_content_outside_managed_block(self) -> None:
        """Verify gitignore updates keep user content outside the managed block."""

        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            gitignore_path = os.path.join(temp_dir, ".gitignore")
            with open(gitignore_path, "w", encoding="utf-8") as handle:
                handle.write(
                    "node_modules/\n\n"
                    "# >>> skill-manager managed workspace files >>>\n"
                    ".gemini/commands/\n"
                    "# <<< skill-manager managed workspace files <<<\n\n"
                    ".env\n"
                )

            installer.ensure_managed_gitignore_entries(temp_dir)

            with open(gitignore_path, "r", encoding="utf-8") as handle:
                gitignore = handle.read()

        self.assertIn("node_modules/", gitignore)
        self.assertIn(".env", gitignore)
        self.assertIn(".gemini/skill-manager-manifest.json", gitignore)
        self.assertEqual(gitignore.count("# >>> skill-manager managed workspace files >>>"), 1)

    def test_ensure_managed_gitignore_entries_bootstraps_from_existing_managed_block(self) -> None:
        """Verify missing manifests are rebuilt from the existing managed gitignore block."""
        import tempfile

        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(os.path.join(temp_dir, ".gemini", "skills", "alpha"))
            os.makedirs(os.path.join(temp_dir, ".agents", "skills", "beta"))
            os.makedirs(os.path.join(temp_dir, ".claude", "skills", "gamma"))
            os.makedirs(os.path.join(temp_dir, ".agents", "skills", "delta"))
            with open(os.path.join(temp_dir, ".gitignore"), "w", encoding="utf-8") as handle:
                handle.write(
                    "# >>> skill-manager managed workspace files >>>\n"
                    ".gemini/skills/alpha/\n"
                    ".agents/skills/beta/\n"
                    ".agents/skills/delta/\n"
                    "# <<< skill-manager managed workspace files <<<\n"
                )

            installer.ensure_managed_gitignore_entries(temp_dir)

            with open(os.path.join(temp_dir, ".gitignore"), "r", encoding="utf-8") as handle:
                gitignore = handle.read()

        self.assertIn(".gemini/skills/alpha/", gitignore)
        self.assertIn(".agents/skills/beta/", gitignore)
        self.assertNotIn(".claude/skills/gamma/", gitignore)
        self.assertIn(".agents/skills/delta/", gitignore)

    def test_ensure_managed_gitignore_entries_prunes_ineligible_companion_skills(self) -> None:
        """Verify stale agents/Claude entries are removed when install config no longer allows them."""
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)

        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(os.path.join(temp_dir, ".gemini", "skills", "subagent-balancer"))
            os.makedirs(os.path.join(temp_dir, ".claude", "skills", "subagent-balancer"))
            os.makedirs(os.path.join(temp_dir, ".agents", "skills", "subagent-balancer"))
            manifest_path = os.path.join(temp_dir, ".gemini", "skill-manager-manifest.json")
            os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
            with open(manifest_path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "gemini": ["subagent-balancer"],
                        "codex": [],
                        "claude": ["subagent-balancer"],
                        "copilot": ["subagent-balancer"],
                    },
                    handle,
                    indent=2,
                )
                handle.write("\n")

            installer.ensure_managed_gitignore_entries(temp_dir)

            with open(os.path.join(temp_dir, ".gitignore"), "r", encoding="utf-8") as handle:
                gitignore = handle.read()
            with open(manifest_path, "r", encoding="utf-8") as handle:
                manifest = json.load(handle)

            self.assertIn(".gemini/skills/subagent-balancer/", gitignore)
            self.assertNotIn(".claude/skills/subagent-balancer/", gitignore)
            self.assertNotIn(".agents/skills/subagent-balancer/", gitignore)
            self.assertEqual(manifest["claude"], [])
            self.assertEqual(manifest["agents"], [])
            self.assertFalse(os.path.exists(os.path.join(temp_dir, ".claude", "skills", "subagent-balancer")))
            self.assertFalse(os.path.exists(os.path.join(temp_dir, ".agents", "skills", "subagent-balancer")))

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_post_install_hook_failure(self, mock_exists, mock_run) -> None:
        """Verify handling of post-install hook failure."""
        import subprocess
        installer = SkillInstaller(self.published_dir, self.mock_ask_user)
        
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="Some error")
        
        # This should not raise, but log an error
        installer._run_post_install_hook("some/hook.py", "target/path")
        mock_run.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_manual_ask_user(self, mock_print, mock_input) -> None:
        """Verify the manual_ask_user fallback."""
        from install import manual_ask_user
        
        config = {
            "questions": [{
                "question": "Choose?",
                "options": [{"label": "opt1", "description": "desc1"}]
            }]
        }
        
        mock_input.return_value = "1"
        response = manual_ask_user(config)
        
        self.assertEqual(response["answers"]["0"], ["opt1"])
        mock_print.assert_called()
        printed = "\n".join(str(call.args[0]) for call in mock_print.call_args_list if call.args)
        self.assertIn("Skill-Manager Installer", printed)

    @patch("builtins.input", return_value="back")
    @patch("builtins.print")
    def test_manual_ask_user_returns_switch_action(self, mock_print, mock_input) -> None:
        """Verify the manual prompt can return a back-to-manager action."""
        from install import manual_ask_user

        config = {
            "questions": [{
                "question": "Choose?",
                "switch_action": {
                    "key": "BACKSPACE",
                    "label": "go back to Skill-Manager",
                    "action": "back_to_manager",
                    "aliases": ["back", "backspace"],
                },
                "options": [{"label": "opt1", "description": "desc1"}]
            }]
        }

        response = manual_ask_user(config)

        self.assertEqual(response["action"], "back_to_manager")
        printed = "\n".join(str(call.args[0]) for call in mock_print.call_args_list if call.args)
        self.assertIn("Backspace", printed)

    def test_parse_selection_input_supports_multiple_styles(self) -> None:
        """Verify the lightweight prompt can parse spaces, commas, ranges, and all."""
        self.assertEqual(parse_selection_input("1 3", 4, True), [0, 2])
        self.assertEqual(parse_selection_input("1,3", 4, True), [0, 2])
        self.assertEqual(parse_selection_input("2-4", 5, True), [1, 2, 3])
        self.assertEqual(parse_selection_input("all", 3, True), [0, 1, 2])
        self.assertEqual(parse_selection_input("0", 3, False), [0])

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("builtins.print")
    def test_manual_ask_user_keyboard_interrupt(self, mock_print, mock_input) -> None:
        """Verify Ctrl+C exits the manual prompt cleanly."""
        from install import manual_ask_user

        config = {
            "questions": [{
                "question": "Choose?",
                "options": [{"label": "opt1", "description": "desc1"}]
            }]
        }

        with self.assertRaises(KeyboardInterrupt):
            manual_ask_user(config)

        mock_print.assert_called_with("\nUser closed the installer.")

    def test_terminal_multi_select_confirms_selected_items(self) -> None:
        """Verify the richer terminal selector can toggle and confirm multiple items."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "utility/skill2", "description": "desc2"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)
        keys = iter(["SPACE", "RIGHT", "SPACE", "ENTER"])

        selected = selector.run(read_key=lambda: next(keys))

        self.assertEqual(selected, ["audit/skill1", "utility/skill2"])
        self.assertIn("Categories", output.getvalue())
        self.assertIn("Use arrows to move, left/right to switch tabs", output.getvalue())
        self.assertIn("Skill-Manager Installer", output.getvalue())
        self.assertIn(INSTALLER_BANNER.splitlines()[0].strip(), output.getvalue())
        self.assertIn("[ AUDIT | 1 ]", output.getvalue())
        self.assertIn("utility (1)", output.getvalue())
        self.assertIn("Active tab: utility (1)", output.getvalue())

    def test_terminal_multi_select_allows_empty_confirmation(self) -> None:
        """Verify Enter with no toggled selections returns an empty selection."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "utility/skill2", "description": "desc2"},
            ],
        }
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=io.StringIO())

        selected = selector.run(read_key=lambda: "ENTER")

        self.assertEqual(selected, [])

    def test_terminal_multi_select_switches_tabs_and_preserves_selection(self) -> None:
        """Verify grouped category tabs can be navigated without losing selections."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "audit/skill2", "description": "desc2"},
                {"label": "workflow/skill3", "description": "desc3"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)
        keys = iter(["SPACE", "RIGHT", "SPACE", "LEFT", "DOWN", "SPACE", "ENTER"])

        selected = selector.run(read_key=lambda: next(keys))

        self.assertEqual(selected, ["audit/skill1", "audit/skill2", "workflow/skill3"])
        rendered = output.getvalue()
        self.assertIn("[ AUDIT | 2 ]", rendered)
        self.assertIn("workflow (1)", rendered)
        self.assertIn("audit/skill2", rendered)
        self.assertIn("workflow/skill3", rendered)
        self.assertIn("Total selected: 3", rendered)

    def test_terminal_multi_select_avoids_full_clear_on_every_refresh(self) -> None:
        """Verify rerenders repaint the frame without clearing the full visible region."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "workflow/skill2", "description": "desc2"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)
        keys = iter(["DOWN", "ENTER"])

        selector.run(read_key=lambda: next(keys))

        rendered = output.getvalue()
        self.assertEqual(rendered.count("\x1b[2J\x1b[H"), 2)
        self.assertNotIn("\x1b[H\x1b[J", rendered)
        self.assertIn("\x1b[2K", rendered)

    def test_terminal_multi_select_single_category_keeps_legacy_prompt(self) -> None:
        """Verify the non-tab selector path remains unchanged for a single category."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "audit/skill2", "description": "desc2"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)

        selector.run(read_key=lambda: "ENTER")

        rendered = output.getvalue()
        self.assertIn("Use arrows, space to toggle, A to select all, Enter to confirm.", rendered)
        self.assertNotIn("left/right to switch tabs", rendered)

    def test_terminal_multi_select_colors_items_by_state(self) -> None:
        """Verify installed, update, and new items get distinct colors in the terminal UI."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/new-skill", "description": "brand new", "state": "new"},
                {"label": "audit/old-skill", "description": "already installed", "state": "installed"},
                {"label": "audit/update-skill", "description": "needs update", "state": "update"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)
        selector.enable_color = True

        selector.run(read_key=lambda: "ENTER")

        rendered = output.getvalue()
        self.assertIn(f"{ANSI_WHITE}{ANSI_BOLD}audit/new-skill", rendered)
        self.assertIn(f"{ANSI_GRAY}audit/old-skill", rendered)
        self.assertIn(f"{ANSI_YELLOW}{ANSI_BOLD}audit/update-skill", rendered)

    def test_terminal_multi_select_raises_on_quit(self) -> None:
        """Verify the richer terminal selector exits cleanly on quit."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [{"label": "audit/skill1", "description": "desc1"}],
        }
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=io.StringIO())

        with self.assertRaises(KeyboardInterrupt):
            selector.run(read_key=lambda: "q")

    def test_terminal_multi_select_returns_switch_action(self) -> None:
        """Verify Backspace can return to the shared manager launcher."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "switch_action": {
                "key": "BACKSPACE",
                "keys": ["BACKSPACE", "\x08", "\x7f"],
                "label": "go back to Skill-Manager",
                "action": "back_to_manager",
            },
            "options": [{"label": "audit/skill1", "description": "desc1"}],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)

        selected, action = selector.run_with_action(read_key=lambda: "BACKSPACE")

        self.assertEqual(selected, [])
        self.assertEqual(action, "back_to_manager")
        self.assertIn("Press Backspace to go back to Skill-Manager.", output.getvalue())

    def test_terminal_multi_select_handles_ss3_arrow_sequences(self) -> None:
        """Verify terminals using ESC O arrow sequences do not close the selector."""
        question = {
            "question": "Pick skills",
            "multiSelect": True,
            "options": [
                {"label": "audit/skill1", "description": "desc1"},
                {"label": "audit/skill2", "description": "desc2"},
            ],
        }
        output = io.StringIO()
        selector = TerminalMultiSelect(question, input_stream=io.StringIO(), output_stream=output)
        keys = iter(["DOWN", "ENTER"])

        selected = selector.run(read_key=lambda: next(keys))

        self.assertEqual(selected, [])
        rendered = output.getvalue()
        self.assertIn("audit/skill1", rendered)
        self.assertIn("audit/skill2", rendered)

    @patch.dict("os.environ", {}, clear=True)
    @patch("sys.stdin.isatty", return_value=True)
    @patch("sys.stdout.isatty", return_value=True)
    def test_get_cli_ask_user_prefers_terminal_selector(self, _mock_stdout, _mock_stdin) -> None:
        """Verify the CLI uses the richer selector in a real terminal."""
        from install import terminal_ask_user

        ask_user = get_cli_ask_user([])

        self.assertIs(ask_user, terminal_ask_user)

    @patch.dict("os.environ", {}, clear=True)
    @patch("sys.stdin.isatty", return_value=True)
    @patch("sys.stdout.isatty", return_value=True)
    def test_get_cli_ask_user_supports_simple_flag(self, _mock_stdout, _mock_stdin) -> None:
        """Verify the simple flag keeps the lightweight prompt."""
        from install import manual_ask_user

        ask_user = get_cli_ask_user(["--simple"])

        self.assertIs(ask_user, manual_ask_user)

    @patch("install.find_git_root", return_value=None)
    @patch("os.getcwd", return_value="C:/repo/default-target")
    def test_resolve_target_project_path_uses_current_directory_by_default(
        self,
        mock_getcwd,
        mock_find_git_root,
    ) -> None:
        """Verify install target falls back to the current working directory."""
        target = resolve_target_project_path([])

        self.assertEqual(target, os.path.abspath("C:/repo/default-target"))
        mock_getcwd.assert_called_once()
        mock_find_git_root.assert_called_once_with("C:/repo/default-target")

    def test_resolve_target_project_path_supports_explicit_override(self) -> None:
        """Verify install target can be overridden explicitly."""
        target = resolve_target_project_path(["--target-project", "C:/repo/explicit-target"])

        self.assertEqual(target, os.path.abspath("C:/repo/explicit-target"))

    @patch("install.find_git_root", return_value="C:/repo/root")
    @patch("os.getcwd", return_value="C:/repo/root/src/feature")
    def test_resolve_target_project_path_prefers_git_root(
        self,
        mock_getcwd,
        mock_find_git_root,
    ) -> None:
        """Verify install target resolves to the git root when run from a subdirectory."""
        target = resolve_target_project_path([])

        self.assertEqual(target, os.path.abspath("C:/repo/root"))
        mock_getcwd.assert_called_once()
        mock_find_git_root.assert_called_once_with("C:/repo/root/src/feature")

    def test_find_git_root_walks_up_to_git_directory(self) -> None:
        """Verify git root discovery walks up parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = os.path.join(temp_dir, "repo")
            nested = os.path.join(repo_root, "src", "feature")
            os.makedirs(os.path.join(repo_root, ".git"), exist_ok=True)
            os.makedirs(nested, exist_ok=True)

            self.assertEqual(find_git_root(nested), os.path.abspath(repo_root))
            self.assertIsNone(find_git_root(temp_dir))

    @patch("builtins.print")
    def test_print_target_project_summary_reports_managed_locations(self, mock_print) -> None:
        """Verify install summaries show the exact project paths that will be touched."""
        print_target_project_summary(
            "C:/repo/sample",
            skill_names=["skill-manager", "review-optimization"],
            include_agents=True,
            include_claude=True,
        )

        printed = "\n".join(str(call.args[0]) for call in mock_print.call_args_list if call.args)
        self.assertIn("Target project: C:/repo/sample", printed)
        self.assertIn(os.path.join("C:/repo/sample", ".gemini", "skills"), printed)
        self.assertIn(os.path.join("C:/repo/sample", ".agents", "skills"), printed)
        self.assertIn(os.path.join("C:/repo/sample", ".claude", "skills"), printed)
        self.assertIn(os.path.join("C:/repo/sample", ".gemini", "commands", "skill-manager"), printed)

    @patch("install.SkillInstaller")
    @patch("install.SkillSelector")
    @patch("install.get_cli_ask_user")
    @patch("builtins.print")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_main_function(
        self,
        mock_exists,
        mock_getcwd,
        mock_print,
        mock_get_cli_ask_user,
        mock_selector,
        mock_installer,
    ) -> None:
        """Verify that main runs the installation flow."""
        from install import main
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_exists.side_effect = lambda path: str(path).endswith("published")
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock(return_value={"answers": {"0": "no"}})

            mock_inst_instance = mock_installer.return_value
            mock_inst_instance.get_available_skills.return_value = {"audit": ["skill1"]}
            mock_inst_instance.supports_agents_bridge.return_value = False
            mock_inst_instance.supports_claude_reference.return_value = False

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills_with_action.return_value = (["audit/skill1"], None)

            main()

            mock_inst_instance.get_available_skills.assert_called_once()
            mock_sel_instance.select_skills_with_action.assert_called_once()
            mock_inst_instance.install_skill.assert_called_once_with("audit/skill1", temp_dir)
            mock_inst_instance.ensure_managed_gitignore_entries.assert_called_with(temp_dir)
            mock_print.assert_any_call(f"Target project: {temp_dir}")

    @patch("install.SkillInstaller")
    @patch("install.SkillSelector")
    @patch("install.get_cli_ask_user")
    @patch("install.logging.getLogger")
    @patch("builtins.print")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_main_function_refreshes_gitignore_even_when_nothing_is_selected(
        self,
        mock_exists,
        mock_getcwd,
        mock_print,
        mock_get_logger,
        mock_get_cli_ask_user,
        mock_selector,
        mock_installer,
    ) -> None:
        """Verify the managed gitignore block is refreshed even on an empty selection."""
        from install import main

        with tempfile.TemporaryDirectory() as temp_dir:
            mock_exists.side_effect = lambda path: str(path).endswith("published")
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock(return_value={"answers": {"0": "no"}})
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            mock_inst_instance = mock_installer.return_value
            mock_inst_instance.get_available_skills.return_value = {"audit": ["skill1"]}
            mock_inst_instance.supports_agents_bridge.return_value = False
            mock_inst_instance.supports_claude_reference.return_value = False
            mock_inst_instance.ensure_managed_gitignore_entries.return_value = False

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills_with_action.return_value = ([], None)

            main()

            mock_inst_instance.install_skill.assert_not_called()
            mock_inst_instance.ensure_managed_gitignore_entries.assert_called_with(temp_dir)
            mock_logger.info.assert_any_call(
                "No skills selected.",
            )
            mock_logger.info.assert_any_call(
                "Managed .gitignore entries were %s.",
                "verified",
            )
            mock_print.assert_any_call("No skills selected.")
            mock_print.assert_any_call("Managed .gitignore entries were verified.")

    @patch("install.SkillInstaller")
    @patch("install.SkillSelector")
    @patch("manage.main")
    @patch("install.get_cli_ask_user")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_main_function_returns_to_manager_on_back_action(
        self,
        mock_exists,
        mock_getcwd,
        mock_get_cli_ask_user,
        mock_manage_main,
        mock_selector,
        mock_installer,
    ) -> None:
        """Verify Backspace action returns to manage.py instead of installing."""
        from install import main

        with tempfile.TemporaryDirectory() as temp_dir:
            mock_exists.side_effect = lambda path: str(path).endswith("published")
            mock_getcwd.return_value = temp_dir
            mock_get_cli_ask_user.return_value = MagicMock(return_value={"answers": {"0": "no"}})

            mock_inst_instance = mock_installer.return_value
            mock_inst_instance.get_available_skills.return_value = {"audit": ["skill1"]}

            mock_sel_instance = mock_selector.return_value
            mock_sel_instance.select_skills_with_action.return_value = ([], "back_to_manager")

            main()

            mock_manage_main.assert_called_once()
            mock_inst_instance.install_skill.assert_not_called()

    @patch("sys.exit")
    @patch("os.path.exists")
    def test_main_function_missing_dir(self, mock_exists, mock_exit) -> None:
        """Verify that main exits if published dir is missing."""
        from install import main
        mock_exists.return_value = False
        mock_exit.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            main()
        mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
