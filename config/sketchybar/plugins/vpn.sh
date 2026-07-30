#!/usr/bin/env bash
# ABOUTME: Displays VPN connection status from HarmonySASE log.
# ABOUTME: Shows VPN[NetworkName] when connected, VPN[Disconnected] greyed out when not.

LOG="${LOG:-$HOME/Library/Logs/HarmonySASE.log}"
COLOR_RED="0xffff4444"
COLOR_GREEN="0xff44ff44"
COLOR_YELLOW="0xffe0af68"
COLOR_GREY="0xff888888"

color_for_network() {
    if [[ "${1,,}" == *prod* ]]; then
        echo "$COLOR_RED"
    else
        echo "$COLOR_GREEN"
    fi
}

# Replay connection events in log order to find the current state. A disconnect
# clears to grey. "Connected to X" and the periodic ping event both name the
# live network (green, or red for prod). "updated to connected" only marks a
# connection whose network name we never saw since the last disconnect (yellow).
color="$COLOR_GREY"
if [[ -f "$LOG" ]]; then
    while IFS= read -r line; do
        if [[ "$line" == *"State changed from connected to disconnected"* ]]; then
            color="$COLOR_GREY"
        elif [[ "$line" == *"Connected to"* ]]; then
            network="${line##*Connected to }"
            color=$(color_for_network "$network")
        elif [[ "$line" == *"Ping event: BI: network"* ]]; then
            network="${line#*\"network_name\" = }"
            network="${network%%;*}"
            network="${network//\"/}"
            if [[ -n "$network" ]]; then
                color=$(color_for_network "$network")
            fi
        elif [[ "$line" == *"updated to connected"* ]]; then
            if [[ "$color" == "$COLOR_GREY" ]]; then
                color="$COLOR_YELLOW"
            fi
        fi
    done < <(grep -E "(State changed from connected to disconnected|Showing notification: Connected to|Connection state label updated to connected|Ping event: BI: network\|ping)" "$LOG")
fi

sketchybar --set "$NAME" icon.color="$color" label.drawing=off
