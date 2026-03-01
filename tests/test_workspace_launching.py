# ABOUTME: Integration tests for workspace launching (ws-launch).
# ABOUTME: Tests scenarios from the workspace-launching spec against real Aerospace.

import time


class TestBasicTemplateLaunch:
    """Requirement: Launch apps from template."""

    def test_apps_placed_on_target_workspace(self, aerospace, ws_launch, test_templates, unused_slots):
        """Scenario: Basic template launch.

        GIVEN templates contains "Test" with apps iTerm and Google Chrome
        WHEN ws-launch Test <slot> TestWs runs
        THEN workspace <slot> contains windows for both iTerm2 and Google Chrome
        AND Aerospace's focused workspace is <slot>
        """
        slot = unused_slots[0]
        _, write = test_templates
        write({"Test": {"apps": ["iTerm", "Google Chrome"]}})

        result = ws_launch("Test", slot, "TestWs")
        assert result.returncode == 0, f"ws-launch failed: {result.stderr}"

        # Give windows time to settle
        time.sleep(2)

        snap = aerospace.snapshot()
        apps = snap.apps_on(slot)
        assert "iTerm2" in apps, f"Expected iTerm2 on workspace {slot}, got: {apps}"
        assert "Google Chrome" in apps, f"Expected Google Chrome on workspace {slot}, got: {apps}"
        assert aerospace.focused_workspace() == slot

    def test_template_not_found(self, ws_launch, test_templates):
        """Scenario: Template not found.

        WHEN ws-launch NonExistent T Test runs
        THEN the command exits with a non-zero exit code
        """
        _, write = test_templates
        write({"Other": {"apps": ["iTerm"]}})

        result = ws_launch("NonExistent", "T")
        assert result.returncode != 0


class TestNoWindowStealing:
    """Requirement: No window stealing."""

    def test_existing_windows_preserved(self, aerospace, ws_launch, test_templates, unused_slots):
        """Scenario: Existing windows preserved.

        GIVEN templates contains "BrowserTest" with app Google Chrome
              with args ["--new-window", "https://example.com"]
        AND workspace <slot_a> has a Google Chrome window with a known window ID
        WHEN ws-launch BrowserTest <slot_b> TestB runs
        THEN workspace <slot_a> still contains the original Chrome window ID
        AND workspace <slot_b> has a different Chrome window ID
        """
        slot_a = unused_slots[0]
        slot_b = unused_slots[1]
        _, write = test_templates

        # First: launch Chrome on slot_a
        write({"Setup": {"apps": [
            {"app": "Google Chrome", "args": ["--new-window", "https://example.com"]},
        ]}})
        result = ws_launch("Setup", slot_a, "SetupWs")
        assert result.returncode == 0, f"Setup launch failed: {result.stderr}"
        time.sleep(2)

        snap_before = aerospace.snapshot()
        chrome_on_a = [w for w in snap_before.windows_on(slot_a) if w.app_name == "Google Chrome"]
        assert len(chrome_on_a) > 0, f"Expected Chrome on {slot_a} after setup"
        original_chrome_id = chrome_on_a[0].window_id

        # Now launch another Chrome workspace on slot_b
        write({"BrowserTest": {"apps": [
            {"app": "Google Chrome", "args": ["--new-window", "https://example.com"]},
        ]}})
        result = ws_launch("BrowserTest", slot_b, "TestB")
        assert result.returncode == 0, f"ws-launch failed: {result.stderr}"
        time.sleep(2)

        snap_after = aerospace.snapshot()

        # Original Chrome window must still be on slot_a
        chrome_ids_on_a = {w.window_id for w in snap_after.windows_on(slot_a) if w.app_name == "Google Chrome"}
        assert original_chrome_id in chrome_ids_on_a, (
            f"Original Chrome window {original_chrome_id} was stolen from {slot_a}. "
            f"Chrome windows on {slot_a}: {chrome_ids_on_a}"
        )

        # slot_b must have a different Chrome window
        chrome_ids_on_b = {w.window_id for w in snap_after.windows_on(slot_b) if w.app_name == "Google Chrome"}
        assert len(chrome_ids_on_b) > 0, f"Expected Chrome on {slot_b}"
        assert original_chrome_id not in chrome_ids_on_b, (
            f"Original Chrome window ended up on both {slot_a} and {slot_b}"
        )


class TestBareStringApp:
    """Requirement: Bare string app entries."""

    def test_bare_string_launches_window(self, aerospace, ws_launch, test_templates, unused_slots):
        """Scenario: Bare string app.

        GIVEN templates contains "Simple" with `- iTerm` as a bare string entry
        WHEN ws-launch Simple <slot> TestSimple runs
        THEN an iTerm2 window is created on workspace <slot>
        """
        slot = unused_slots[0]
        _, write = test_templates
        write({"Simple": {"apps": ["iTerm"]}})

        result = ws_launch("Simple", slot, "TestSimple")
        assert result.returncode == 0, f"ws-launch failed: {result.stderr}"

        time.sleep(2)

        snap = aerospace.snapshot()
        apps = snap.apps_on(slot)
        assert "iTerm2" in apps, f"Expected iTerm2 on workspace {slot}, got: {apps}"
