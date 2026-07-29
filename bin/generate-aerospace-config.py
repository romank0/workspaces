#!/usr/bin/env python3
# ABOUTME: Reads Aerospace default config and applies workspace-centric modifications.
# ABOUTME: Outputs modified config to ~/.config/aerospace/aerospace.toml.

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import tomli_w

AEROSPACE_DEFAULT = Path("/Applications/AeroSpace.app/Contents/Resources/default-config.toml")
AEROSPACE_CONFIG_DIR = Path.home() / ".config" / "aerospace"
AEROSPACE_CONFIG = AEROSPACE_CONFIG_DIR / "aerospace.toml"

REPO_DIR = Path(__file__).resolve().parent.parent

STATE_DIR = Path.home() / ".local" / "state" / "workspaces"
# Modifier prefix rewrite: every binding fires with the hyper trio held down.
BINDING_PREFIX = "alt-"
HYPER_PREFIX = "alt-cmd-ctrl-"
# Top gap that clears the camera isle (notch) on the built-in retina display
# while casting, when macOS no longer reserves the notch area. Tune as needed.
NOTCH_GAP = 32


def cast_mode_state_path():
    return Path(os.environ.get("CAST_MODE_STATE", str(STATE_DIR / "cast_mode")))


def read_cast_mode():
    return cast_mode_state_path().exists()


def compute_top_gap(monitor_count, cast_mode):
    if monitor_count > 1:
        return [{"monitor": {"main": 28}}, 0]
    return NOTCH_GAP if cast_mode else 0


def remap_binding_prefix(bindings):
    return {
        (HYPER_PREFIX + key[len(BINDING_PREFIX):] if key.startswith(BINDING_PREFIX) else key): action
        for key, action in bindings.items()
    }


def load_default_config():
    if not AEROSPACE_DEFAULT.exists():
        print(f"ERROR: Aerospace default config not found at {AEROSPACE_DEFAULT}", file=sys.stderr)
        sys.exit(1)
    with open(AEROSPACE_DEFAULT, "rb") as f:
        return tomllib.load(f)


def get_monitor_count():
    result = subprocess.run(
        ["aerospace", "list-monitors", "--count"],
        capture_output=True, text=True, timeout=5, check=True,
    )
    return int(result.stdout.strip())


def apply_modifications(config):
    monitor_count = get_monitor_count()

    config["default-root-container-layout"] = "accordion"
    config["default-root-container-orientation"] = "vertical"

    ws_sync = str(REPO_DIR / "bin" / "ws-sync")
    config["after-startup-command"] = [f"exec-and-forget {ws_sync}"]

    config["exec-on-workspace-change"] = [
        '/bin/bash', '-c',
        'sketchybar --trigger aerospace_workspace_change'
        ' FOCUSED=$AEROSPACE_FOCUSED_WORKSPACE'
        ' PREV=$AEROSPACE_PREV_WORKSPACE'
    ]

    config["gaps"]["outer"]["top"] = compute_top_gap(monitor_count, read_cast_mode())
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

    # Cast mode: toggles a notch-clearing top gap for screen mirroring
    ws_cast = str(REPO_DIR / "bin" / "ws-cast")
    config["mode"]["main"]["binding"]["alt-shift-c"] = f"exec-and-forget {ws_cast} toggle"

    for mode in config["mode"].values():
        if "binding" in mode:
            mode["binding"] = remap_binding_prefix(mode["binding"])

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
