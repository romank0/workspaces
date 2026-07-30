#!/usr/bin/env bash
# ABOUTME: Displays VPN connection status from HarmonySASE log.
# ABOUTME: Shows VPN[NetworkName] when connected, VPN[Disconnected] greyed out when not.

LOG="${LOG:-$HOME/Library/Logs/HarmonySASE.log}"
COLOR_RED="0xffff4444"
COLOR_GREEN="0xff44ff44"
COLOR_YELLOW="0xffe0af68"
COLOR_GREY="0xff888888"

# Replay connect/disconnect events in log order to find the current state.
# A disconnect clears to grey. "Connected to X" gives a named connection
# (green, or red for prod). "updated to connected" only marks a connection
# whose network name we never saw since the last disconnect (yellow).
color="$COLOR_GREY"
if [[ -f "$LOG" ]]; then
    while IFS= read -r line; do
        if [[ "$line" == *"State changed from connected to disconnected"* ]]; then
            color="$COLOR_GREY"
        elif [[ "$line" == *"Connected to"* ]]; then
            network="${line##*Connected to }"
            if [[ "${network,,}" == *prod* ]]; then
                color="$COLOR_RED"
            else
                color="$COLOR_GREEN"
            fi
        elif [[ "$line" == *"updated to connected"* ]]; then
            if [[ "$color" == "$COLOR_GREY" ]]; then
                color="$COLOR_YELLOW"
            fi
        fi
    done < <(grep -E "(State changed from connected to disconnected|Showing notification: Connected to|Connection state label updated to connected)" "$LOG")
fi

sketchybar --set "$NAME" icon.color="$color" label.drawing=off
