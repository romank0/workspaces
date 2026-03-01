# ABOUTME: Integration tests for workspace launching (ws-launch).
# ABOUTME: Tests scenarios from the workspace-launching spec against real Aerospace.

import subprocess
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


class TestDisplayNamePersistence:
    """Requirement: Display name persistence."""

    def test_name_saved_on_launch(self, ws_launch, test_templates, test_name_store, unused_slots):
        """Scenario: Name saved on launch.

        GIVEN templates contains "Minimal" with app iTerm
        WHEN ws-launch Minimal <slot> MyWorkspace runs
        THEN the name store contains line "<slot>=MyWorkspace"
        """
        slot = unused_slots[0]
        _, write = test_templates
        write({"Minimal": {"apps": ["iTerm"]}})

        result = ws_launch("Minimal", slot, "MyWorkspace")
        assert result.returncode == 0, f"ws-launch failed: {result.stderr}"

        contents = test_name_store.read_text()
        assert f"{slot}=MyWorkspace" in contents

    def test_name_overwritten_on_relaunch(self, ws_launch, test_templates, test_name_store, unused_slots):
        """Scenario: Name overwritten on relaunch.

        GIVEN slot <slot> has name "OldName" in the name store
        AND templates contains "Minimal" with app iTerm
        WHEN ws-launch Minimal <slot> NewName runs
        THEN the name store contains "<slot>=NewName"
        AND the name store does NOT contain "<slot>=OldName"
        """
        slot = unused_slots[0]
        _, write = test_templates
        write({"Minimal": {"apps": ["iTerm"]}})

        # Seed with old name
        test_name_store.parent.mkdir(parents=True, exist_ok=True)
        test_name_store.write_text(f"{slot}=OldName\n")

        result = ws_launch("Minimal", slot, "NewName")
        assert result.returncode == 0, f"ws-launch failed: {result.stderr}"

        contents = test_name_store.read_text()
        assert f"{slot}=NewName" in contents
        assert f"{slot}=OldName" not in contents


class TestBrowserUrlSupport:
    """Requirement: Browser URL support."""

    def test_chrome_window_with_url(self, aerospace, ws_launch, test_templates, unused_slots):
        """Scenario: Chrome window with URL.

        GIVEN templates contains "Web" with app Google Chrome
              and args ["--new-window", "https://example.com"]
        WHEN ws-launch Web <slot> TestWeb runs
        THEN a new Google Chrome window is created on workspace <slot>
        AND the active tab URL contains "example.com"
        """
        slot = unused_slots[0]
        _, write = test_templates
        write({"Web": {"apps": [
            {"app": "Google Chrome", "args": ["--new-window", "https://example.com"]},
        ]}})

        result = ws_launch("Web", slot, "TestWeb")
        assert result.returncode == 0, f"ws-launch failed: {result.stderr}"
        time.sleep(2)

        snap = aerospace.snapshot()
        chrome_on_slot = [w for w in snap.windows_on(slot) if w.app_name == "Google Chrome"]
        assert len(chrome_on_slot) > 0, f"Expected Chrome on workspace {slot}"

        # Verify URL via AppleScript
        url_result = subprocess.run(
            ["osascript", "-e",
             f'tell application "Google Chrome" to get URL of active tab of window id {chrome_on_slot[0].window_id}'],
            capture_output=True, text=True, timeout=5,
        )
        if url_result.returncode == 0:
            assert "example.com" in url_result.stdout, (
                f"Expected URL containing 'example.com', got: {url_result.stdout.strip()}"
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
