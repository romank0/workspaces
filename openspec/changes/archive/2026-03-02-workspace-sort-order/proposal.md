## Why

Workspaces in SketchyBar currently appear in Aerospace's default alphanumeric order (1-9, A-Z). This doesn't match keyboard layout, so visually scanning the bar to find a workspace requires mental mapping between letter position and keyboard position. Sorting by keyboard row order (1234567890, qwert, asdf, zxcv) makes the bar match physical key positions.

## What Changes

- ws-sync sorts workspace items by a configurable key order before rendering to SketchyBar
- A default sort order matching QWERTY keyboard layout is provided
- The sort order is configurable via environment variable

## Capabilities

### New Capabilities
- `workspace-sort-order`: Configurable ordering of workspace items in SketchyBar by a defined key sequence

### Modified Capabilities
- `workspace-display`: ws-sync item creation order changes from Aerospace default to sorted order

## Impact

- `bin/ws-sync`: item loop needs to sort slots before rendering
- No API or dependency changes
- No breaking changes — existing behavior changes to keyboard-layout order by default
