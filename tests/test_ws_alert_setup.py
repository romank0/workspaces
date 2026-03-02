# ABOUTME: Tests for ws-alert-setup that configures Claude Code hooks.
# ABOUTME: Uses isolated settings files to avoid modifying real Claude config.

import json
import subprocess
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
WS_ALERT_SETUP = str(REPO_DIR / "bin" / "ws-alert-setup")
WS_ALERT_PATH = str(REPO_DIR / "bin" / "ws-alert")


@pytest.fixture
def settings_file(tmp_path):
    """Isolated Claude settings file."""
    path = tmp_path / "settings.json"
    path.write_text("{}")
    return path


def run_setup(*args, settings_file):
    import os

    env = os.environ.copy()
    env["WS_ALERT_SETTINGS_FILE"] = str(settings_file)

    return subprocess.run(
        [WS_ALERT_SETUP, *args],
        capture_output=True, text=True, timeout=5, env=env,
    )


def test_adds_stop_and_prompt_hooks(settings_file):
    result = run_setup("--global", settings_file=settings_file)
    assert result.returncode == 0, result.stderr

    settings = json.loads(settings_file.read_text())
    hooks = settings["hooks"]

    assert "Stop" in hooks
    assert "UserPromptSubmit" in hooks

    stop_commands = [
        h["command"]
        for group in hooks["Stop"]
        for h in group["hooks"]
    ]
    assert any("ws-alert on" in cmd for cmd in stop_commands)

    prompt_commands = [
        h["command"]
        for group in hooks["UserPromptSubmit"]
        for h in group["hooks"]
    ]
    assert any("ws-alert off" in cmd for cmd in prompt_commands)


def test_idempotent(settings_file):
    run_setup("--global", settings_file=settings_file)
    run_setup("--global", settings_file=settings_file)

    settings = json.loads(settings_file.read_text())
    stop_groups = settings["hooks"]["Stop"]
    ws_alert_groups = [
        g for g in stop_groups
        if any("ws-alert" in h["command"] for h in g["hooks"])
    ]
    assert len(ws_alert_groups) == 1


def test_preserves_existing_hooks(settings_file):
    existing = {
        "hooks": {
            "PreCompact": [
                {
                    "matcher": "",
                    "hooks": [{"type": "command", "command": "bd prime"}],
                }
            ]
        }
    }
    settings_file.write_text(json.dumps(existing))

    result = run_setup("--global", settings_file=settings_file)
    assert result.returncode == 0, result.stderr

    settings = json.loads(settings_file.read_text())
    assert "PreCompact" in settings["hooks"]
    assert settings["hooks"]["PreCompact"] == existing["hooks"]["PreCompact"]
    assert "Stop" in settings["hooks"]


def test_remove_hooks(settings_file):
    run_setup("--global", settings_file=settings_file)
    result = run_setup("--global", "--remove", settings_file=settings_file)
    assert result.returncode == 0, result.stderr

    settings = json.loads(settings_file.read_text())
    hooks = settings.get("hooks", {})

    if "Stop" in hooks:
        for group in hooks["Stop"]:
            for h in group["hooks"]:
                assert "ws-alert" not in h["command"]

    if "UserPromptSubmit" in hooks:
        for group in hooks["UserPromptSubmit"]:
            for h in group["hooks"]:
                assert "ws-alert" not in h["command"]
