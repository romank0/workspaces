## Why

The `ws-alert on` hook fires when Claude Code stops, but it often marks the wrong workspace. The alert appears on whichever workspace is focused at the moment the hook fires, not the workspace where Claude's terminal actually lives. This makes the alert useless — switching workspaces while Claude is working causes alerts to land on the wrong slot.

The root cause is likely in `detect_terminal_workspace`: the iTerm session-to-window lookup may be failing silently, falling back to `aerospace list-workspaces --focused`, which returns wherever the user happens to be looking.

## What Changes

- Investigate and fix `detect_terminal_workspace` so it reliably identifies the workspace containing the terminal that triggered the hook
- Ensure alerts are never placed on the focused workspace as a fallback when the terminal is on a different workspace

## Capabilities

### New Capabilities

### Modified Capabilities
- `workspace-display`: alert state must correctly associate with the terminal's workspace, not the focused workspace

## Impact

- `bin/ws-alert`: `detect_terminal_workspace` function needs debugging/fixing
- May need to pass workspace identity through the hook mechanism differently if iTerm session lookup is unreliable
