# Cast Mode — design

## Problem

When screen mirroring / casting from the built-in retina display, macOS stops
reserving the notch (camera isle) area, so window manager windows extend to the
very top of the screen and overflow the SketchyBar. There is no way to reclaim
that space without editing the Aerospace config by hand.

## Goal

A keyboard shortcut (`alt-shift-c`) toggles "cast mode." While cast mode is on,
the built-in retina display's top gap grows from `0` to a notch-clearing value
so windows sit below the SketchyBar and camera isle. A SketchyBar icon shows
when the mode is active.

## Mechanism

Aerospace modes only swap key bindings — gaps are global config and cannot be
made mode-specific. So cast mode is a state toggle, not an Aerospace
binding-mode:

1. The keybinding runs `ws-cast toggle`.
2. `ws-cast` flips a state file, regenerates `aerospace.toml`, and runs
   `aerospace reload-config`.
3. `generate-aerospace-config.py` reads the state file and chooses the top gap
   accordingly.

This mirrors the existing `passthrough` state-file pattern and reuses
`generate-aerospace-config.py`'s existing monitor-count branch.

## Components

### State file

`~/.local/state/workspaces/cast_mode` — present means on, absent means off.
Lives in the same state dir as `alerts/` and the `aerospace_mode` file. Path is
overridable via an environment variable for tests.

### `bin/ws-cast`

Toggle script following the structure and env-var conventions of `bin/ws-alert`.

Subcommands:

- `on` — create the state file.
- `off` — remove the state file.
- `toggle` — flip the state file.
- `status` — exit 0 if cast mode is on, 1 if not.

After a state change, `ws-cast` regenerates the config via the venv Python, runs
`aerospace reload-config`, and triggers the `cast_mode_change` SketchyBar event.
These side effects are skipped when a `WS_CAST_SKIP_REFRESH`-style env flag is
set (mirroring `ws-alert`'s `WS_ALERT_SKIP_REFRESH`) so state transitions can be
tested in isolation.

The keybinding calls `ws-cast toggle`.

### `generate-aerospace-config.py`

Additions:

- `NOTCH_GAP = 37` constant — the notch-clearing top gap (tune later).
- `read_cast_mode()` — reads the state file; path overridable via env, like
  `NAME_STORE`.
- `compute_top_gap(monitor_count, cast_mode)` — pure function returning the top
  gap value, unit-testable without Aerospace:
  - single monitor + cast on → `NOTCH_GAP`
  - single monitor + cast off → `0` (current behavior)
  - multi-monitor → `[{"monitor": {"main": 28}}, 0]` (unchanged)
- `alt-shift-c` binding in `mode.main` → `exec-and-forget <repo>/bin/ws-cast toggle`.

### SketchyBar indicator

- New `cast` item in `sketchybarrc`, subscribed to a new `cast_mode_change`
  event.
- New `config/sketchybar/plugins/cast.sh` that reads the state file and sets
  `drawing=on` with a cast icon when active, `drawing=off` otherwise.
- `ws-cast` triggers `cast_mode_change` after toggling.

## Testing

- Unit-test `compute_top_gap` across the three cases (no Aerospace needed).
- Test `ws-cast` state transitions (`toggle`, `on`, `off`, `status`) with an
  isolated state dir, skipping reload/refresh side effects via the env flag.

## Persistence

`watch-displays` already regenerates the config when the monitor count changes.
Because `generate-aerospace-config.py` reads the state file, cast mode survives
those regenerations automatically — no extra handling needed.

## Out of scope (YAGNI)

- Cast mode affecting the multi-monitor branch (the notch only matters on the
  built-in retina display, and mirroring keeps monitor count at 1).
- Auto-detecting mirroring to toggle the mode automatically.
