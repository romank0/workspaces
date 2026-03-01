# ABOUTME: Integration tests for the workspace picker (ws-pick).
# ABOUTME: Tests scenarios from the workspace-picker spec against real Aerospace.

import os
import subprocess
import threading
import time
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent


class TestActiveWorkspaceListing:
    """Requirement: Active workspace listing."""

    def test_occupied_workspaces_shown(self, aerospace, ws_pick, ws_launch, test_templates, test_name_store, unused_slots):
        """Scenario: Multiple active workspaces.

        GIVEN workspaces <slot_a> and <slot_b> have windows
        AND slot <slot_a> has display name "MyWork" in the name store
        WHEN ws-pick builds its entry list
        THEN entries include both workspaces
        AND <slot_a>'s entry shows "MyWork" as its label
        """
        slot_a = unused_slots[0]
        slot_b = unused_slots[1]
        _, write = test_templates
        write({"TestTmpl": {"apps": ["iTerm"]}})

        # Launch windows on both slots
        result_a = ws_launch("TestTmpl", slot_a, "MyWork")
        assert result_a.returncode == 0, f"Launch A failed: {result_a.stderr}"
        time.sleep(2)

        result_b = ws_launch("TestTmpl", slot_b, "Other")
        assert result_b.returncode == 0, f"Launch B failed: {result_b.stderr}"
        time.sleep(2)

        # Set up display name for slot_a
        test_name_store.parent.mkdir(parents=True, exist_ok=True)
        test_name_store.write_text(f"{slot_a}=MyWork\n{slot_b}=Other\n")

        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        # Both slots should appear in the entry list
        slot_entries = [l for l in lines if l.startswith(("*", " ")) and not l.startswith("~") and not l.startswith("+")]
        slot_ids = [l[2:].split()[0] for l in slot_entries]
        assert slot_a in slot_ids, f"Expected {slot_a} in entries: {slot_entries}"
        assert slot_b in slot_ids, f"Expected {slot_b} in entries: {slot_entries}"

        # slot_a should show display name "MyWork"
        slot_a_entry = [l for l in slot_entries if l[2:].split()[0] == slot_a][0]
        assert "MyWork" in slot_a_entry

    def test_empty_workspaces_excluded(self, ws_pick, test_templates, unused_slots):
        """Scenario: Empty workspaces excluded.

        GIVEN workspace <slot> has no windows and is not focused
        WHEN ws-pick builds its entry list
        THEN no entry for <slot> appears
        """
        empty_slot = unused_slots[0]
        _, write = test_templates
        write({"Dummy": {"apps": ["iTerm"]}})

        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        slot_entries = [l for l in lines if l.startswith(("*", " ")) and not l.startswith("~") and not l.startswith("+")]
        slot_ids = [l[2:].split()[0] for l in slot_entries]
        assert empty_slot not in slot_ids, f"Empty slot {empty_slot} should not appear"


class TestFocusedWorkspaceMarker:
    """Requirement: Focused workspace marker."""

    def test_focused_has_star_prefix(self, aerospace, ws_pick, test_templates):
        """Scenario: Focused workspace highlighted.

        GIVEN workspace <focused> is the focused workspace
        WHEN ws-pick builds its entry list
        THEN <focused>'s entry starts with *
        AND other entries start with space
        """
        _, write = test_templates
        write({"Dummy": {"apps": ["iTerm"]}})

        focused = aerospace.focused_workspace()
        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        workspace_entries = [l for l in lines if l.strip().startswith(("*", " ")) and not l.startswith(("~", "+"))]

        focused_entries = [l for l in workspace_entries if l.startswith("*")]
        assert len(focused_entries) >= 1, "Expected at least one focused entry"

        # The focused entry should contain the focused workspace slot
        focused_line = focused_entries[0]
        assert focused in focused_line, f"Expected focused slot {focused} in '{focused_line}'"

        # Non-focused entries should start with space
        other_entries = [l for l in workspace_entries if l.startswith(" ")]
        for entry in other_entries:
            assert not entry.startswith("*"), f"Non-focused entry should not have *: {entry}"


class TestTemplateListing:
    """Requirement: Template listing."""

    def test_templates_shown(self, ws_pick, test_templates):
        """Scenario: Templates shown.

        GIVEN templates contains "Dev" and "Ops"
        WHEN ws-pick builds its entry list
        THEN entries include `+ New from Dev` and `+ New from Ops`
        """
        _, write = test_templates
        write({
            "Dev": {"apps": ["iTerm"]},
            "Ops": {"apps": ["iTerm"]},
        })

        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        assert "+ New from Dev" in lines
        assert "+ New from Ops" in lines


class TestTerminalEntry:
    """Requirement: Terminal workspace creation."""

    def test_terminal_entry_present(self, ws_pick, test_templates):
        """The picker SHALL show a `+ Terminal` entry for quick terminal workspace creation."""
        _, write = test_templates
        write({"Dummy": {"apps": ["iTerm"]}})

        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        assert "+ Terminal" in lines


class TestRenameEntry:
    """Requirement: Rename workspace."""

    def test_rename_entry_present(self, ws_pick, test_templates):
        """The picker SHALL show a `~ Rename` entry when the focused workspace has windows."""
        _, write = test_templates
        write({"Dummy": {"apps": ["iTerm"]}})

        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        assert "~ Rename" in lines


class TestSlotAvailability:
    """Requirement: Slot availability."""

    def test_used_slots_excluded_from_entries(self, aerospace, ws_pick, test_templates):
        """Scenario: Used slots excluded.

        GIVEN some workspaces have windows
        WHEN ws-pick builds its entry list
        THEN only workspaces with windows appear as switchable entries
        AND empty slots do NOT appear as workspace entries
        """
        _, write = test_templates
        write({"Dummy": {"apps": ["iTerm"]}})

        occupied = aerospace.occupied_workspaces()

        result = ws_pick("--list")
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")

        workspace_entries = [l for l in lines if l.startswith(("*", " ")) and not l.startswith(("~", "+"))]
        listed_slots = {l[2:].split()[0] for l in workspace_entries}

        # All listed slots should be occupied
        for slot in listed_slots:
            assert slot in occupied, f"Slot {slot} listed but has no windows"


def send_keystroke(text, delay=0.3):
    """Send keystrokes to the frontmost application via System Events."""
    time.sleep(delay)
    subprocess.run(
        ["osascript", "-e",
         f'tell application "System Events"\n'
         f'  keystroke "{text}"\n'
         f'  delay 0.3\n'
         f'  keystroke return\n'
         f'end tell'],
        capture_output=True, timeout=5,
    )


def wait_for_choose(timeout=5):
    """Wait for a choose-gui process to appear."""
    for _ in range(timeout * 4):
        result = subprocess.run(["pgrep", "-x", "choose"], capture_output=True)
        if result.returncode == 0:
            return True
        time.sleep(0.25)
    return False


def automate_create_flow(template_filter, slot, name):
    """Background thread: automates three successive choose-gui prompts."""
    # Step 1: select template
    if not wait_for_choose():
        return
    send_keystroke(template_filter)

    # Step 2: select slot
    if not wait_for_choose():
        return
    send_keystroke(slot)

    # Step 3: enter name
    if not wait_for_choose():
        return
    # Name prompt has a default value pre-filled; clear it first
    subprocess.run(
        ["osascript", "-e",
         'tell application "System Events"\n'
         '  keystroke "a" using command down\n'
         '  delay 0.1\n'
         f'  keystroke "{name}"\n'
         '  delay 0.3\n'
         '  keystroke return\n'
         'end tell'],
        capture_output=True, timeout=5,
    )


@pytest.mark.ui
class TestPickerUI:
    """End-to-end UI test using real choose-gui."""

    def test_create_from_template_via_ui(self, aerospace, test_templates, test_name_store, unused_slots):
        """Full UI flow: select template → pick slot → enter name → workspace created.

        This test opens real choose-gui windows and sends keystrokes via System Events.
        Run with: pytest -m ui
        """
        slot = unused_slots[0]
        _, write = test_templates
        write({"UITest": {"apps": ["iTerm", "Google Chrome"]}})

        before_ids = aerospace.snapshot().window_ids()

        # Start automation thread before launching picker
        auto_thread = threading.Thread(
            target=automate_create_flow,
            args=("UITest", slot, "AutoTest"),
        )
        auto_thread.start()

        # Run ws-pick with real choose-gui but isolated templates/name store
        env = os.environ.copy()
        env["TEMPLATES_FILE"] = str(test_templates[0])
        env["NAME_STORE"] = str(test_name_store)

        result = subprocess.run(
            [str(REPO_DIR / "bin" / "ws-pick")],
            capture_output=True, text=True, timeout=30, env=env,
        )

        auto_thread.join(timeout=5)

        assert result.returncode == 0, f"ws-pick failed: {result.stderr}"

        # Give launched apps time to create windows
        time.sleep(3)

        snap = aerospace.snapshot()
        apps = snap.apps_on(slot)
        assert "iTerm2" in apps, f"Expected iTerm2 on workspace {slot}, got: {apps}"
        assert "Google Chrome" in apps, f"Expected Google Chrome on workspace {slot}, got: {apps}"

        # Verify display name was saved
        assert test_name_store.exists(), "Name store should exist"
        contents = test_name_store.read_text()
        assert f"{slot}=AutoTest" in contents

        # Cleanup: close windows created during test
        current_ids = aerospace.snapshot().window_ids()
        for wid in current_ids - before_ids:
            try:
                aerospace.close_window(wid)
            except Exception:
                pass
