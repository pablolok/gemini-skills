---
name: skill-manager
description: Manage and install official Gemini skills from the global skills repository.
---

# Skill Manager

This skill allows Gemini to manage and install official skills into the current project by interacting with the `install.py` script from the global `gemini-skills` repository.

## Usage

### 1. List Available Skills
To see what's available, you must first locate the `gemini-skills` repository on the user's machine.

**Search Pattern:** `**/gemini-skills/install.py`

Once found, you can scan for skills:
```python
from install import SkillInstaller
installer = SkillInstaller("<path-to-gemini-skills>/published", ask_user_fn)
available = installer.get_available_skills()
```

### 2. Install Skills
To install a skill, use the `SkillInstaller` and `SkillSelector` logic.

```python
# 1. Ask user to select from 'available'
# 2. For each selected skill_path:
installer.install_skill(skill_path, os.getcwd())
```

### 3. Check for Updates
To check if installed skills have newer versions available in the global repository:

```python
updates = installer.check_for_updates(os.getcwd())
if updates:
    # Notify user about available updates
    # Each item in 'updates' has: name, installed, latest, rel_path
```

### 4. Update Skills
To update a skill, simply reinstall it. The installer will handle overwriting existing files and cleaning up legacy junctions.

```python
for update in updates:
    installer.install_skill(update['rel_path'], os.getcwd())
```

## Integration
This skill ensures that official skills are properly physically copied into the target project and their `post_install.py` hooks are executed to maintain project-level workflow consistency. The use of file copying (replacing legacy junctions) enables robust version tracking and update notifications.
