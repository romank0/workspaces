#!/usr/bin/env bash
# ABOUTME: Shows a cast icon in SketchyBar while cast mode is active.
# ABOUTME: Reads the cast_mode state file written by ws-cast.

STATE_FILE="${STATE_FILE:-$HOME/.local/state/workspaces/cast_mode}"

if [[ -f "$STATE_FILE" ]]; then
    sketchybar --set "$NAME" drawing=on
else
    sketchybar --set "$NAME" drawing=off
fi
