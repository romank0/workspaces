# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A macOS workspace environment manager that ties together Aerospace (tiling window manager), SketchyBar (menu bar), iTerm2, and Google Chrome. Workspaces are persistent slots (1-9, A-Z) that each hold a set of app windows. Users switch contexts by switching workspaces.

## Commands

```bash
bin/setup                        # Install everything: venv, configs, symlinks, reload services
pytest                           # Run all tests (excludes UI tests)
pytest -m ui                     # Run GUI-only tests
pytest tests/test_ws_alert.py    # Run a single test file
pytest -k test_name              # Run a single test by name
```

Dependencies: `aerospace`, `sketchybar`, `jq`, `yq`, `fzf`, `python3` (all via Homebrew).

Python venv (`.venv/`) is created by `bin/setup` for TOML manipulation (`tomli_w`). Tests also need `pytest` and `pyyaml`.

## Architecture

**Core flow:** User triggers picker → `ws-pick` shows menu → `ws-launch` creates workspace from template → Aerospace fires workspace-change event → `ws-sync` rebuilds SketchyBar items.

**Scripts (`bin/`):**
- `ws-pick` / `ws-pick-wrapper` — interactive workspace picker (uses `choose-gui` or fzf)
- `ws-launch` — launches apps from a template into a workspace slot
- `ws-sync` — reads Aerospace state, updates SketchyBar workspace items
- `ws-alert` / `ws-alert-setup` — marks workspaces for visual highlighting (amber color)
- `generate-aerospace-config.py` — generates Aerospace TOML from app defaults + modifications
- `setup` — full installation: deps, venv, config generation, symlinks, service reload

**State (`~/.local/state/workspaces/`):**
- `names` — flat-file display name store (`SLOT=NAME` lines), shared via `lib/name-store.sh`
- `alerts/` — one file per alerted workspace slot
- `sessions/` — maps iTerm session IDs to workspace slots

**Templates (`templates/workspaces.yaml`):** Defines workspace types with app lists. Apps can be bare strings or objects with `args`, `profile-tag` (iTerm2), or `chrome-profile`.

**Config (`config/`):** SketchyBar config (symlinked to `~/.config/sketchybar`) and iTerm2 dynamic profile for the picker popup.

## Testing

Tests are integration tests that interact with real Aerospace and iTerm2 instances — no mocking. Key fixtures in `conftest.py`:
- `ws_launch(template, slot)` — runs ws-launch with isolated state, cleans up windows on teardown
- `ws_pick(*args, choose_cmd=None)` — runs ws-pick with isolated templates
- `unused_slots` — returns available slots (prefers T-Z to avoid multi-monitor conflicts)
- `test_templates` — returns `(path, write_fn)` for temporary template files

Environment variables `TEMPLATES_FILE`, `NAME_STORE`, and `CHOOSE_CMD` are used by tests to isolate state.

## Conventions

- Shell scripts use `set -euo pipefail` and include `ABOUTME:` comment headers describing purpose.
- Slots "1" and "2" are persistent monitor workspaces, always shown in SketchyBar.
- SketchyBar workspace items are sorted by QWERTY keyboard layout position.
