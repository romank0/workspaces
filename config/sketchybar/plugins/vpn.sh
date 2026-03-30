#!/usr/bin/env bash
# ABOUTME: Displays VPN connection status from HarmonySASE log.
# ABOUTME: Shows VPN[NetworkName] when connected, VPN[Disconnected] greyed out when not.

LOG="${LOG:-$HOME/Library/Logs/HarmonySASE.log}"
COLOR_RED="0xffff4444"
COLOR_GREEN="0xff44ff44"
COLOR_YELLOW="0xffe0af68"
COLOR_GREY="0xff888888"

if [[ -f "$LOG" ]]; then
    last_line=$(grep -E "(State changed from connected to disconnected|Showing notification: Connected to)" "$LOG" | tail -1)
    # Fallback: if no primary status lines found, check for connection state
    if [[ -z "$last_line" ]]; then
        last_line=$(grep -E "(State changed from connected to disconnected|Connection state label updated to connected)" "$LOG" | tail -1)
    fi
fi

if [[ "$last_line" == *"Connected to"* ]]; then
    network="${last_line##*Connected to }"
    local_lower="${network,,}"
    if [[ "$local_lower" == *prod* ]]; then
        color="$COLOR_RED"
    else
        color="$COLOR_GREEN"
    fi
elif [[ "$last_line" == *"updated to connected"* ]]; then
    color="$COLOR_YELLOW"
else
    color="$COLOR_GREY"
fi

sketchybar --set "$NAME" icon.color="$color" label.drawing=off
