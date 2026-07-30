# ABOUTME: Tests for SketchyBar plugin scripts.
# ABOUTME: Uses a mock sketchybar binary to capture --set calls from each plugin.

import os
import subprocess
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_DIR / "config" / "sketchybar" / "plugins"
MOCK_SKETCHYBAR = str(REPO_DIR / "tests" / "helpers" / "mock-sketchybar")


@pytest.fixture
def plugin_env(tmp_path):
    """Returns a function that runs a plugin script with mock sketchybar on PATH."""
    mock_bin = tmp_path / "bin"
    mock_bin.mkdir()
    (mock_bin / "sketchybar").symlink_to(MOCK_SKETCHYBAR)

    log_file = tmp_path / "sketchybar.log"

    def run(plugin_name, env_extras=None):
        env = os.environ.copy()
        env["PATH"] = f"{mock_bin}:{env['PATH']}"
        env["NAME"] = "test_item"
        env["MOCK_SKETCHYBAR_LOG"] = str(log_file)
        if env_extras:
            env.update(env_extras)

        result = subprocess.run(
            [str(PLUGINS_DIR / plugin_name)],
            capture_output=True, text=True, timeout=5, env=env,
        )
        output = log_file.read_text() if log_file.exists() else ""
        return result, output

    return run


# --- keyboard.sh tests ---


class TestKeyboardPlugin:
    def test_shows_layout_label(self, plugin_env):
        result, output = plugin_env("keyboard.sh")
        assert result.returncode == 0
        assert "--set test_item label=" in output


# --- vpn.sh tests ---


class TestVpnPlugin:
    def test_connected_non_prod(self, plugin_env, tmp_path):
        log = tmp_path / "vpn.log"
        log.write_text(
            "26-03-25 11:39:32.547 DEBUG [AGT] "
            "MainSubController.onConnectedToVPN_handler():635 "
            "- Showing notification: Connected to JikoStaff\n"
        )
        result, output = plugin_env("vpn.sh", env_extras={"LOG": str(log)})
        assert result.returncode == 0
        assert "icon.color=0xff44ff44" in output  # green

    def test_connected_prod(self, plugin_env, tmp_path):
        log = tmp_path / "vpn.log"
        log.write_text(
            "26-03-25 11:39:32.547 DEBUG [AGT] "
            "MainSubController.onConnectedToVPN_handler():635 "
            "- Showing notification: Connected to ProdNetwork\n"
        )
        result, output = plugin_env("vpn.sh", env_extras={"LOG": str(log)})
        assert result.returncode == 0
        assert "icon.color=0xffff4444" in output  # red

    def test_disconnected(self, plugin_env, tmp_path):
        log = tmp_path / "vpn.log"
        log.write_text(
            "26-03-25 11:31:21.395 DEBUG [AGT] "
            "StatusItemController.state:24 "
            "- State changed from connected to disconnected\n"
        )
        result, output = plugin_env("vpn.sh", env_extras={"LOG": str(log)})
        assert result.returncode == 0
        assert "icon.color=0xff888888" in output  # grey

    def test_reconnect_after_disconnect_without_notification(self, plugin_env, tmp_path):
        # A reconnect that only logs "updated to connected" (no "Connected to X")
        # after an earlier disconnect must show connected, not stale grey.
        log = tmp_path / "vpn.log"
        log.write_text(
            "26-07-30 13:58:31.296 DEBUG [AGT] "
            "StatusItemController.state:35 "
            "- State changed from connected to disconnected\n"
            "26-07-30 19:00:23.635 DEBUG [AGT] "
            "MainSubController.onConnectedToVPN_handler():672 "
            "- Connection state label updated to connected\n"
        )
        result, output = plugin_env("vpn.sh", env_extras={"LOG": str(log)})
        assert result.returncode == 0
        assert "icon.color=0xffe0af68" in output  # yellow (connected, network unknown)

    def test_connect_notification_then_label_update_stays_named(self, plugin_env, tmp_path):
        # A normal connect logs "Connected to X" then "updated to connected".
        # The trailing label-update must not downgrade the known network color.
        log = tmp_path / "vpn.log"
        log.write_text(
            "26-07-30 05:16:28.471 DEBUG [AGT] "
            "MainSubController.onConnectedToVPN_handler():635 "
            "- Showing notification: Connected to JikoStaff\n"
            "26-07-30 05:16:28.473 DEBUG [AGT] "
            "MainSubController.onConnectedToVPN_handler():648 "
            "- Connection state label updated to connected\n"
        )
        result, output = plugin_env("vpn.sh", env_extras={"LOG": str(log)})
        assert result.returncode == 0
        assert "icon.color=0xff44ff44" in output  # green

    def test_disconnect_after_connect_is_grey(self, plugin_env, tmp_path):
        # A disconnect following a named connect must clear back to grey.
        log = tmp_path / "vpn.log"
        log.write_text(
            "26-07-30 07:00:28.624 DEBUG [AGT] "
            "MainSubController.onConnectedToVPN_handler():635 "
            "- Showing notification: Connected to JikoStaff\n"
            "26-07-30 13:58:31.296 DEBUG [AGT] "
            "StatusItemController.state:35 "
            "- State changed from connected to disconnected\n"
        )
        result, output = plugin_env("vpn.sh", env_extras={"LOG": str(log)})
        assert result.returncode == 0
        assert "icon.color=0xff888888" in output  # grey

    def test_missing_log_file(self, plugin_env, tmp_path):
        result, output = plugin_env(
            "vpn.sh",
            env_extras={"LOG": str(tmp_path / "nonexistent.log")},
        )
        assert result.returncode == 0
        assert "icon.color=0xff888888" in output  # grey


# --- slack.sh tests ---


class TestSlackPlugin:
    def test_no_notifications(self, plugin_env, tmp_path):
        mock_osascript = tmp_path / "bin" / "osascript"
        mock_osascript.write_text("#!/bin/bash\necho 'missing value'\n")
        mock_osascript.chmod(0o755)
        result, output = plugin_env("slack.sh")
        # osascript may fail in test env — that's the "missing value" path
        assert result.returncode == 0
        assert "label.drawing=off" in output

    def test_dot_notification(self, plugin_env, tmp_path):
        mock_osascript = tmp_path / "bin" / "osascript"
        mock_osascript.write_text("#!/bin/bash\necho '•'\n")
        mock_osascript.chmod(0o755)
        result, output = plugin_env("slack.sh")
        assert result.returncode == 0
        assert "icon.color=0xffcc3b3b" in output  # dark red

    def test_number_notification(self, plugin_env, tmp_path):
        mock_osascript = tmp_path / "bin" / "osascript"
        mock_osascript.write_text("#!/bin/bash\necho '5'\n")
        mock_osascript.chmod(0o755)
        result, output = plugin_env("slack.sh")
        assert result.returncode == 0
        assert "label=5" in output
        assert "label.color=0xffff4444" in output  # red


# --- mail.sh tests ---


class TestMailPlugin:
    def test_no_mail(self, plugin_env, tmp_path):
        mock_osascript = tmp_path / "bin" / "osascript"
        mock_osascript.write_text("#!/bin/bash\necho 'missing value'\n")
        mock_osascript.chmod(0o755)
        result, output = plugin_env("mail.sh")
        assert result.returncode == 0
        assert "label.drawing=off" in output

    def test_unread_count(self, plugin_env, tmp_path):
        mock_osascript = tmp_path / "bin" / "osascript"
        mock_osascript.write_text("#!/bin/bash\necho '12'\n")
        mock_osascript.chmod(0o755)
        result, output = plugin_env("mail.sh")
        assert result.returncode == 0
        assert "label=12" in output
        assert "label.color=0xffff4444" in output
