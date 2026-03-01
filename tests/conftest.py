# ABOUTME: Shared fixtures for integration tests.
# ABOUTME: Provides helpers to query and manage Aerospace window/workspace state.

import json
import os
import subprocess
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml

REPO_DIR = Path(__file__).resolve().parent.parent
# Prefer high letter slots for tests to avoid multi-monitor workspace conflicts
TEST_PREFERRED_SLOTS = [chr(c) for c in range(ord("T"), ord("Z") + 1)]
ALL_SLOTS = [str(i) for i in range(1, 10)] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]


@dataclass
class Window:
    window_id: int
    app_name: str
    workspace: str


@dataclass
class StateSnapshot:
    windows: list[Window] = field(default_factory=list)

    def window_ids(self) -> set[int]:
        return {w.window_id for w in self.windows}

    def windows_on(self, workspace: str) -> list[Window]:
        return [w for w in self.windows if w.workspace == workspace]

    def apps_on(self, workspace: str) -> set[str]:
        return {w.app_name for w in self.windows_on(workspace)}


class Aerospace:
    """Thin wrapper around the aerospace CLI for test assertions."""

    @staticmethod
    def run(*args: str) -> str:
        result = subprocess.run(
            ["aerospace", *args],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()

    def snapshot(self) -> StateSnapshot:
        raw = self.run(
            "list-windows", "--all", "--json",
            "--format", "%{window-id}%{tab}%{app-name}%{tab}%{workspace}",
        )
        if not raw:
            return StateSnapshot()
        entries = json.loads(raw)
        windows = [
            Window(
                window_id=int(e["window-id"]),
                app_name=e["app-name"],
                workspace=e["workspace"],
            )
            for e in entries
        ]
        return StateSnapshot(windows=windows)

    def focused_workspace(self) -> str:
        return self.run("list-workspaces", "--focused")

    def occupied_workspaces(self) -> set[str]:
        snap = self.snapshot()
        return {w.workspace for w in snap.windows}

    def switch_workspace(self, slot: str):
        self.run("workspace", slot)

    def close_window(self, window_id: int):
        self.run("close", "--window-id", str(window_id))


@pytest.fixture
def aerospace():
    return Aerospace()


@pytest.fixture
def repo_dir():
    return REPO_DIR


@pytest.fixture
def unused_slots(aerospace):
    """Returns a list of workspace slots that currently have no windows.

    Prefers high letter slots (T-Z) to avoid multi-monitor workspace conflicts.
    """
    occupied = aerospace.occupied_workspaces()
    focused = aerospace.focused_workspace()
    occupied.add(focused)
    preferred = [s for s in TEST_PREFERRED_SLOTS if s not in occupied]
    rest = [s for s in ALL_SLOTS if s not in occupied and s not in TEST_PREFERRED_SLOTS]
    return preferred + rest


@pytest.fixture
def test_templates(tmp_path):
    """Creates a temporary templates file. Returns (path, write_fn).

    Usage:
        templates_file, write = test_templates
        write({"MyTemplate": {"apps": ["iTerm"]}})
    """
    templates_file = tmp_path / "workspaces.yaml"

    def write(data: dict):
        templates_file.write_text(yaml.dump(data, default_flow_style=False))

    return templates_file, write


@pytest.fixture
def test_name_store(tmp_path):
    """Returns path to an isolated name store file for testing."""
    return tmp_path / "names"


@pytest.fixture
def ws_launch(aerospace, test_templates, test_name_store, unused_slots):
    """Runs ws-launch with isolated templates and name store.

    Returns a callable: ws_launch(template, slot, display_name=None) -> CompletedProcess

    Tracks all windows created during the test and closes them on teardown.
    Restores focused workspace on teardown.
    """
    templates_file, _ = test_templates
    original_focus = aerospace.focused_workspace()
    before_ids = aerospace.snapshot().window_ids()
    created_window_ids = []

    def run(template: str, slot: str, display_name: str | None = None, timeout: int = 30):
        args = [str(REPO_DIR / "bin" / "ws-launch"), template, slot]
        if display_name is not None:
            args.append(display_name)

        env = os.environ.copy()
        env["TEMPLATES_FILE"] = str(templates_file)
        env["NAME_STORE"] = str(test_name_store)

        result = subprocess.run(
            args,
            capture_output=True, text=True, timeout=timeout, env=env,
        )

        # Track new windows for cleanup
        current_ids = aerospace.snapshot().window_ids()
        new_ids = current_ids - before_ids - set(created_window_ids)
        created_window_ids.extend(new_ids)

        return result

    yield run

    # Cleanup: close windows created during test
    for wid in created_window_ids:
        try:
            aerospace.close_window(wid)
        except Exception:
            pass

    # Restore focus
    try:
        aerospace.switch_workspace(original_focus)
    except Exception:
        pass


@pytest.fixture
def ws_pick(test_templates, test_name_store):
    """Runs ws-pick with isolated templates and name store.

    Returns a callable: ws_pick(*args, choose_cmd=None) -> CompletedProcess
    """
    templates_file, _ = test_templates

    def run(*args: str, choose_cmd: str | None = None, timeout: int = 10):
        cmd = [str(REPO_DIR / "bin" / "ws-pick"), *args]

        env = os.environ.copy()
        env["TEMPLATES_FILE"] = str(templates_file)
        env["NAME_STORE"] = str(test_name_store)
        if choose_cmd is not None:
            env["CHOOSE_CMD"] = choose_cmd

        return subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=timeout, env=env,
        )

    return run
