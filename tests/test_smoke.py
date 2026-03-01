# ABOUTME: Smoke tests verifying the test infrastructure works with real Aerospace.
# ABOUTME: These tests don't test project behavior, only that we can observe system state.


def test_aerospace_is_running(aerospace):
    """Verify aerospace CLI is accessible and responds."""
    workspace = aerospace.focused_workspace()
    assert workspace, "Aerospace should report a focused workspace"


def test_snapshot_returns_windows(aerospace):
    """Verify we can snapshot window state."""
    snap = aerospace.snapshot()
    assert len(snap.windows) > 0, "There should be at least one window open"


def test_snapshot_has_workspace_info(aerospace):
    """Verify snapshots include workspace assignment for each window."""
    snap = aerospace.snapshot()
    for window in snap.windows:
        assert window.workspace, f"Window {window.window_id} ({window.app_name}) should have a workspace"


def test_snapshot_window_ids_are_unique(aerospace):
    """Verify window IDs are unique across the snapshot."""
    snap = aerospace.snapshot()
    ids = [w.window_id for w in snap.windows]
    assert len(ids) == len(set(ids)), "Window IDs should be unique"


def test_windows_on_filters_correctly(aerospace):
    """Verify the windows_on helper filters by workspace."""
    snap = aerospace.snapshot()
    focused = aerospace.focused_workspace()
    focused_windows = snap.windows_on(focused)
    assert all(
        w.workspace == focused for w in focused_windows
    ), "windows_on should only return windows from the specified workspace"
