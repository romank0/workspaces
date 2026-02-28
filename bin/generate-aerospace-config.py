#!/usr/bin/env python3
# ABOUTME: Reads Aerospace default config and applies workspace-centric modifications.
# ABOUTME: Outputs modified config to ~/.config/aerospace/aerospace.toml.

import sys
import tomllib
from pathlib import Path

import tomli_w

AEROSPACE_DEFAULT = Path("/Applications/AeroSpace.app/Contents/Resources/default-config.toml")
AEROSPACE_CONFIG_DIR = Path.home() / ".config" / "aerospace"
AEROSPACE_CONFIG = AEROSPACE_CONFIG_DIR / "aerospace.toml"

REPO_DIR = Path(__file__).resolve().parent.parent


def load_default_config():
    if not AEROSPACE_DEFAULT.exists():
        print(f"ERROR: Aerospace default config not found at {AEROSPACE_DEFAULT}", file=sys.stderr)
        sys.exit(1)
    with open(AEROSPACE_DEFAULT, "rb") as f:
        return tomllib.load(f)


def apply_modifications(config):
    config["default-root-container-layout"] = "accordion"

    ws_sync = str(REPO_DIR / "bin" / "ws-sync")
    config["after-startup-command"] = [f"exec-and-forget {ws_sync}"]

    sketchybar_trigger = (
        'sketchybar --trigger aerospace_workspace_change'
        ' FOCUSED=$AEROSPACE_FOCUSED_WORKSPACE'
        ' PREV=$AEROSPACE_PREV_WORKSPACE'
    )
    config["exec-on-workspace-change"] = [
        f'exec-and-forget bash -c "{sketchybar_trigger}"'
    ]

    config["gaps"]["outer"]["top"] = 36

    config["persistent-workspaces"] = ["1"]

    # Add alt-space to open workspace picker
    picker_cmd = (
        "exec-and-forget osascript -e "
        "'tell application \"iTerm\" to create window with profile \"Workspace Picker\" "
        "command \"" + str(REPO_DIR / "bin" / "ws-pick") + "\"'"
    )
    config["mode"]["main"]["binding"]["alt-space"] = picker_cmd

    return config


def write_config(config):
    AEROSPACE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(AEROSPACE_CONFIG, "wb") as f:
        tomli_w.dump(config, f)
    print(f"Generated {AEROSPACE_CONFIG}")


def main():
    config = load_default_config()
    config = apply_modifications(config)
    write_config(config)


if __name__ == "__main__":
    main()
