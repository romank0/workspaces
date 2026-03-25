#!/usr/bin/env bash
# ABOUTME: Displays current keyboard layout as a short label.
# ABOUTME: Shows UA for Ukrainian, PL for Polish, otherwise first two letters.
# ABOUTME: Appends a native character when Aerospace passthrough mode is active.

STATE_FILE="${STATE_FILE:-$HOME/.local/state/workspaces/aerospace_mode}"

# Update persisted mode on mode-change event
if [[ "$SENDER" == "aerospace_mode_change" ]]; then
    mkdir -p "$(dirname "$STATE_FILE")"
    echo "$MODE" > "$STATE_FILE"
fi

current_mode=$(cat "$STATE_FILE" 2>/dev/null)

layout=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources 2>/dev/null \
    | grep -i "KeyboardLayout Name" \
    | sed 's/.*= "\(.*\)";/\1/')

lower="${layout,,}"

if [[ "$lower" == *ukr* ]]; then
    label="UA"
    [[ "$current_mode" == "passthrough" ]] && label="UAы"
elif [[ "$lower" == *polish* ]]; then
    label="PL"
    [[ "$current_mode" == "passthrough" ]] && label="PLą"
else
    label="${layout:0:2}"
fi

sketchybar --set "$NAME" label="$label"
