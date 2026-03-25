#!/usr/bin/env bash
# ABOUTME: Displays bluetooth on/off status as icon color.
# ABOUTME: White when on, greyed out when off.

COLOR_WHITE="0xffffffff"
COLOR_GREY="0xff888888"

status=$(system_profiler SPBluetoothDataType 2>/dev/null | grep -i "State:")

if [[ "$status" == *"On"* ]]; then
    sketchybar --set "$NAME" icon.color="$COLOR_WHITE"
else
    sketchybar --set "$NAME" icon.color="$COLOR_GREY"
fi
