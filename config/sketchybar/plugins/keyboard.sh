#!/usr/bin/env bash
# ABOUTME: Displays current keyboard layout as a short label.
# ABOUTME: Shows UA for Ukrainian, PL for Polish, otherwise first two letters.

layout=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources 2>/dev/null \
    | grep -i "KeyboardLayout Name" \
    | sed 's/.*= "\(.*\)";/\1/')

lower="${layout,,}"

if [[ "$lower" == *ukr* ]]; then
    label="UA"
elif [[ "$lower" == *polish* ]]; then
    label="PL"
else
    label="${layout:0:2}"
fi

sketchybar --set "$NAME" label="$label"
