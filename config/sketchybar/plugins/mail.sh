#!/usr/bin/env bash
# ABOUTME: Displays Apple Mail unread count from Dock badge.
# ABOUTME: Shows count in red when unread, greyed out dash when none.

COLOR_RED="0xffff4444"
COLOR_GREY="0xff888888"

value=$(osascript -e 'tell application "System Events" to tell process "Dock" to get value of attribute "AXStatusLabel" of UI element "Mail" of list 1' 2>/dev/null)

if [[ "$value" == "missing value" || -z "$value" ]]; then
    sketchybar --set "$NAME" label="-" label.color="$COLOR_GREY"
elif [[ "$value" == "•" ]]; then
    sketchybar --set "$NAME" label="*" label.color="$COLOR_RED"
else
    sketchybar --set "$NAME" label="$value" label.color="$COLOR_RED"
fi
