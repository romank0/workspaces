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
