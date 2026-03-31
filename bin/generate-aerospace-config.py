#!/usr/bin/env python3
# ABOUTME: Reads Aerospace default config and applies workspace-centric modifications.
# ABOUTME: Outputs modified config to ~/.config/aerospace/aerospace.toml.

import subprocess
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


def get_monitor_count():
    try:
        result = subprocess.run(
            ["aerospace", "list-monitors", "--count"],
            capture_output=True, text=True, timeout=5,
        )
        return int(result.stdout.strip())
    except Exception:
        return 1


def apply_modifications(config):
    monitor_count = get_monitor_count()

    config["default-root-container-layout"] = "accordion"
    config["default-root-container-orientation"] = "vertical"

    ws_sync = str(REPO_DIR / "bin" / "ws-sync")
    watch_displays = str(REPO_DIR / "bin" / "watch-displays")
    config["after-startup-command"] = [
        f"exec-and-forget {ws_sync}",
        f"exec-and-forget {watch_displays}",
    ]

    config["exec-on-workspace-change"] = [
        '/bin/bash', '-c',
        'sketchybar --trigger aerospace_workspace_change'
        ' FOCUSED=$AEROSPACE_FOCUSED_WORKSPACE'
        ' PREV=$AEROSPACE_PREV_WORKSPACE'
    ]

    if monitor_count > 1:
        config["gaps"]["outer"]["top"] = [
            {"monitor": {"main": 28}},
            0,
        ]
    else:
        config["gaps"]["outer"]["top"] = 0
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

    # Vim-style focus with wrapping in all directions
    config["mode"]["main"]["binding"]["alt-h"] = "focus left --boundaries-action wrap-around-the-workspace"
    config["mode"]["main"]["binding"]["alt-j"] = "focus down --boundaries-action wrap-around-the-workspace"
    config["mode"]["main"]["binding"]["alt-k"] = "focus up --boundaries-action wrap-around-the-workspace"
    config["mode"]["main"]["binding"]["alt-l"] = "focus right --boundaries-action wrap-around-the-workspace"

    picker = str(REPO_DIR / "bin" / "ws-pick")
    config["mode"]["main"]["binding"]["alt-enter"] = f"exec-and-forget {picker}"

    # Passthrough mode: disables all Aerospace bindings for typing special characters
    state_file = str(Path.home() / ".local/state/workspaces/aerospace_mode")
    config["mode"]["main"]["binding"]["alt-shift-backtick"] = [
        f"exec-and-forget echo passthrough > {state_file}",
        "mode passthrough",
    ]
    config["mode"]["passthrough"] = {"binding": {"alt-shift-backtick": [
        f"exec-and-forget echo main > {state_file}",
        "mode main",
    ]}}
    config.pop("on-mode-changed", None)

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
