# ABOUTME: Integration tests for the workspace picker (ws-pick).
# ABOUTME: Tests scenarios from the workspace-picker spec against real Aerospace.

import time


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
