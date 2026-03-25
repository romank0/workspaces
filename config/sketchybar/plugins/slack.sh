#!/usr/bin/env bash
# ABOUTME: Displays Slack notification badge count from Dock status label.
# ABOUTME: Shows Slack[count] in red, Slack[*] for unread, Slack[-] greyed out for none.

COLOR_RED="0xffff4444"
COLOR_DARK_RED="0xffcc3b3b"
COLOR_WHITE="0xffffffff"
COLOR_GREY="0xff888888"

value=$(osascript -e 'tell application "System Events" to tell process "Dock" to get value of attribute "AXStatusLabel" of UI element "Slack" of list 1' 2>/dev/null)

if [[ "$value" == "missing value" || -z "$value" ]]; then
    sketchybar --set "$NAME" label.drawing=off icon.color="$COLOR_GREY"
elif [[ "$value" == "•" ]]; then
    sketchybar --set "$NAME" label.drawing=off icon.color="$COLOR_DARK_RED"
else
    sketchybar --set "$NAME" label="$value" label.drawing=on label.color="$COLOR_RED" icon.color="$COLOR_WHITE"
fi
