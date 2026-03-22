# Skill Manager

Manage and install official Gemini skills from the global skills repository.

## Features

- **Interactive Installation**: Use `install.py` to select and install skills.
- **Update Checking**: Use `check_updates.py` to see if your installed skills are out of date.
- **Post-Installation Hooks**: Automatically executes `post_install.py` for project-specific setup.
- **Physical Copying**: Replaces legacy junctions with robust file copying for better version tracking.

## Usage

### Install/Update Skills
Run the installer from your project's root:
```bash
python <path-to-gemini-skills>/install.py
```

### Check for Updates
Run the update checker from your project's root:
```bash
python <path-to-gemini-skills>/check_updates.py
```

## Post-Installation Hooks

Skills can include a `post_install.py` script that will be executed after installation. This is commonly used by skills like `review-optimization` to inject protocol entries into `conductor/workflow.md`.
