#!/usr/bin/env bash
# ABOUTME: Displays VPN connection status from HarmonySASE log.
# ABOUTME: Shows VPN[NetworkName] when connected, VPN[Disconnected] greyed out when not.

LOG="$HOME/Library/Logs/HarmonySASE.log"
COLOR_RED="0xffff4444"
COLOR_GREEN="0xff44ff44"
COLOR_GREY="0xff888888"

if [[ -f "$LOG" ]]; then
    last_line=$(grep -E "(State changed from connected to disconnected|Showing notification: Connected to)" "$LOG" | tail -1)
fi

if [[ "$last_line" == *"Connected to"* ]]; then
    network="${last_line##*Connected to }"
    local_lower="${network,,}"
    if [[ "$local_lower" == *prod* ]]; then
        color="$COLOR_RED"
    else
        color="$COLOR_GREEN"
    fi
    sketchybar --set "$NAME" label="$network" label.color="$color"
else
    sketchybar --set "$NAME" label="Disconnected" label.color="$COLOR_GREY"
fi
