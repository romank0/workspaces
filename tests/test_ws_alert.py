# ABOUTME: Tests for the ws-alert script that toggles workspace alert state.
# ABOUTME: Uses isolated state directory to avoid affecting real workspace state.

import subprocess
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
WS_ALERT = str(REPO_DIR / "bin" / "ws-alert")


@pytest.fixture
def state_dir(tmp_path):
    """Isolated state directory for ws-alert."""
    return tmp_path


def run_ws_alert(*args, state_dir, env_extras=None):
    """Run ws-alert with isolated state directory."""
    import os

    env = os.environ.copy()
    env["WS_ALERT_STATE_DIR"] = str(state_dir)
    # Prevent sketchybar trigger during tests
    env["WS_ALERT_SKIP_REFRESH"] = "1"
    if env_extras:
        env.update(env_extras)

    return subprocess.run(
        [WS_ALERT, *args],
        capture_output=True, text=True, timeout=5, env=env,
    )


def test_alert_on_creates_state_file(state_dir):
    result = run_ws_alert("on", "T", state_dir=state_dir)
    assert result.returncode == 0
    alert_file = state_dir / "alert"
    assert alert_file.exists()
    assert alert_file.read_text().strip() == "T"


def test_alert_on_defaults_to_terminal_workspace(state_dir, aerospace):
    """No-arg 'on' should detect the terminal's workspace, not the focused one."""
    terminal_ws = aerospace.focused_workspace()
    result = run_ws_alert("on", state_dir=state_dir)
    assert result.returncode == 0
    alert_file = state_dir / "alert"
    assert alert_file.read_text().strip() == terminal_ws


def test_alert_on_uses_terminal_workspace_not_focused(state_dir, aerospace, unused_slots):
    """When focus is elsewhere, 'on' should still target the terminal's workspace."""
    terminal_ws = aerospace.focused_workspace()
    other_ws = unused_slots[0]
    aerospace.switch_workspace(other_ws)
    try:
        result = run_ws_alert("on", state_dir=state_dir)
        assert result.returncode == 0, result.stderr
        alert_file = state_dir / "alert"
        assert alert_file.read_text().strip() == terminal_ws
    finally:
        aerospace.switch_workspace(terminal_ws)


def test_alert_off_removes_state_file(state_dir):
    alert_file = state_dir / "alert"
    alert_file.write_text("T")
    result = run_ws_alert("off", state_dir=state_dir)
    assert result.returncode == 0
    assert not alert_file.exists()


def test_alert_off_noop_when_no_file(state_dir):
    result = run_ws_alert("off", state_dir=state_dir)
    assert result.returncode == 0


def test_alert_status_active(state_dir):
    alert_file = state_dir / "alert"
    alert_file.write_text("T")
    result = run_ws_alert("status", state_dir=state_dir)
    assert result.returncode == 0


def test_alert_status_inactive(state_dir):
    result = run_ws_alert("status", state_dir=state_dir)
    assert result.returncode == 1
