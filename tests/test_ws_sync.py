# ABOUTME: Tests for workspace bar synchronization (ws-sync).
# ABOUTME: Tests sorting and rendering logic for SketchyBar workspace items.

import json
import subprocess


QWERTY_ORDER = "1234567890QWERTYUIOPASDFGHJKLZXCVBNM"

SORT_JQ = (
    '[.[] | .workspace as $w | . + {"_idx": ($order | index($w) // 999)}]'
    ' | sort_by(._idx) | .[].workspace'
)


def test_slots_sorted_by_qwerty_order():
    """Slots should be ordered by QWERTY keyboard row position."""
    entries = json.dumps([
        {"workspace": "Z"}, {"workspace": "A"}, {"workspace": "1"},
        {"workspace": "W"}, {"workspace": "2"}, {"workspace": "Q"},
    ])

    result = subprocess.run(
        ["jq", "-r", "--arg", "order", QWERTY_ORDER, SORT_JQ],
        input=entries, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip().splitlines() == ["1", "2", "Q", "W", "A", "Z"]


def test_unlisted_slots_sort_last():
    """Slots not in the sort order appear after listed ones."""
    entries = json.dumps([
        {"workspace": "Z"}, {"workspace": "1"},
    ])

    # Use a short order that only includes "1"
    result = subprocess.run(
        ["jq", "-r", "--arg", "order", "1", SORT_JQ],
        input=entries, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip().splitlines() == ["1", "Z"]
