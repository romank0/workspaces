#!/usr/bin/env bash
# ABOUTME: Displays audio output device as speaker or headphones icon.
# ABOUTME: Uses SwitchAudioSource to detect current output device.

ICON_SPEAKER="󰕾"
ICON_HEADPHONES="󰋋"

device=$(SwitchAudioSource -c 2>/dev/null)

if [[ "$device" == "MacBook Pro Speakers" ]]; then
    sketchybar --set "$NAME" icon="$ICON_SPEAKER"
else
    sketchybar --set "$NAME" icon="$ICON_HEADPHONES"
fi
