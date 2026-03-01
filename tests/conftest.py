# ABOUTME: Shared fixtures for integration tests.
# ABOUTME: Provides helpers to query and manage Aerospace window/workspace state.

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent


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
