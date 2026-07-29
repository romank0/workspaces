# ABOUTME: Unit tests for gap and cast-mode logic in generate-aerospace-config.py.
# ABOUTME: Pure functions tested without touching Aerospace.

import importlib.util
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
SCRIPT = REPO_DIR / "bin" / "generate-aerospace-config.py"


@pytest.fixture
def gen():
    spec = importlib.util.spec_from_file_location("generate_aerospace_config", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_single_monitor_cast_off_has_no_gap(gen):
    assert gen.compute_top_gap(1, cast_mode=False) == 0


def test_single_monitor_cast_on_uses_notch_gap(gen):
    assert gen.compute_top_gap(1, cast_mode=True) == gen.NOTCH_GAP


def test_multi_monitor_unaffected_by_cast_off(gen):
    assert gen.compute_top_gap(2, cast_mode=False) == [{"monitor": {"main": 28}}, 0]


def test_multi_monitor_unaffected_by_cast_on(gen):
    assert gen.compute_top_gap(2, cast_mode=True) == [{"monitor": {"main": 28}}, 0]


def test_read_cast_mode_false_when_no_file(gen, tmp_path, monkeypatch):
    monkeypatch.setenv("CAST_MODE_STATE", str(tmp_path / "cast_mode"))
    assert gen.read_cast_mode() is False


def test_read_cast_mode_true_when_file_present(gen, tmp_path, monkeypatch):
    state = tmp_path / "cast_mode"
    state.touch()
    monkeypatch.setenv("CAST_MODE_STATE", str(state))
    assert gen.read_cast_mode() is True


def test_remap_prefix_rewrites_plain_alt(gen):
    assert gen.remap_binding_prefix({"alt-h": "focus left"}) == {
        "alt-cmd-ctrl-h": "focus left"
    }


def test_remap_prefix_rewrites_alt_shift(gen):
    assert gen.remap_binding_prefix({"alt-shift-h": "move left"}) == {
        "alt-cmd-ctrl-shift-h": "move left"
    }


def test_remap_prefix_leaves_non_alt_keys_untouched(gen):
    bindings = {"esc": ["reload-config", "mode main"], "r": ["flatten-workspace-tree"]}
    assert gen.remap_binding_prefix(bindings) == bindings


def test_remap_prefix_preserves_list_actions(gen):
    assert gen.remap_binding_prefix({"alt-shift-backtick": ["echo main", "mode main"]}) == {
        "alt-cmd-ctrl-shift-backtick": ["echo main", "mode main"]
    }
