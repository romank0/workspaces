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

    config["exec-on-workspace-change"] = [
        '/bin/bash', '-c',
        'sketchybar --trigger aerospace_workspace_change'
        ' FOCUSED=$AEROSPACE_FOCUSED_WORKSPACE'
        ' PREV=$AEROSPACE_PREV_WORKSPACE'
    ]

    config["gaps"]["outer"]["top"] = [
        {"monitor": {"main": 36}},
        0,
    ]
    config["accordion-padding"] = 0

    config["persistent-workspaces"] = ["1", "2"]

    config["workspace-to-monitor-force-assignment"] = {
        "1": "main",
        "2": "secondary",
    }

    config.setdefault("on-window-detected", []).append({
        "if": {"window-title-regex-substring": "Workspace Picker"},
        "run": "layout floating",
    })

    # Accordion cycling: override default up/down to left/right
    config["mode"]["main"]["binding"]["alt-j"] = "focus left --boundaries-action wrap-around-the-workspace"
    config["mode"]["main"]["binding"]["alt-k"] = "focus right --boundaries-action wrap-around-the-workspace"

    picker = str(REPO_DIR / "bin" / "ws-pick")
    config["mode"]["main"]["binding"]["alt-enter"] = f"exec-and-forget {picker}"

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
