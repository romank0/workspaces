# ABOUTME: Tests for the ws-cast script that toggles cast-mode state.
# ABOUTME: Uses isolated state directory and skips config reload side effects.

import os
import subprocess
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
WS_CAST = str(REPO_DIR / "bin" / "ws-cast")


@pytest.fixture
def state_dir(tmp_path):
    return tmp_path


def run_ws_cast(*args, state_dir):
    env = os.environ.copy()
    env["WS_CAST_STATE_DIR"] = str(state_dir)
    env["WS_CAST_SKIP_REFRESH"] = "1"
    return subprocess.run(
        [WS_CAST, *args],
        capture_output=True, text=True, timeout=5, env=env,
    )


def cast_on(state_dir):
    return (state_dir / "cast_mode").exists()


def test_on_creates_state_file(state_dir):
    result = run_ws_cast("on", state_dir=state_dir)
    assert result.returncode == 0, result.stderr
    assert cast_on(state_dir)


def test_off_removes_state_file(state_dir):
    run_ws_cast("on", state_dir=state_dir)
    result = run_ws_cast("off", state_dir=state_dir)
    assert result.returncode == 0
    assert not cast_on(state_dir)


def test_off_noop_when_not_set(state_dir):
    result = run_ws_cast("off", state_dir=state_dir)
    assert result.returncode == 0
    assert not cast_on(state_dir)


def test_toggle_turns_on_when_off(state_dir):
    result = run_ws_cast("toggle", state_dir=state_dir)
    assert result.returncode == 0
    assert cast_on(state_dir)


def test_toggle_turns_off_when_on(state_dir):
    run_ws_cast("on", state_dir=state_dir)
    result = run_ws_cast("toggle", state_dir=state_dir)
    assert result.returncode == 0
    assert not cast_on(state_dir)


def test_on_idempotent(state_dir):
    run_ws_cast("on", state_dir=state_dir)
    run_ws_cast("on", state_dir=state_dir)
    assert cast_on(state_dir)


def test_status_active(state_dir):
    run_ws_cast("on", state_dir=state_dir)
    result = run_ws_cast("status", state_dir=state_dir)
    assert result.returncode == 0


def test_status_inactive(state_dir):
    result = run_ws_cast("status", state_dir=state_dir)
    assert result.returncode == 1
