#!/usr/bin/env bash
# ABOUTME: Displays audio output device icon and volume percentage.
# ABOUTME: Shows speaker icon for built-in speakers, headphones icon otherwise.

ICON_SPEAKER="󰕾"
ICON_HEADPHONES="󰋋"

device=$(SwitchAudioSource -c 2>/dev/null)

if [[ "$device" == "MacBook Pro Speakers" ]]; then
    icon="$ICON_SPEAKER"
else
    icon="$ICON_HEADPHONES"
fi

if [[ "$SENDER" == "volume_change" ]]; then
    sketchybar --set "$NAME" icon="$icon" label="${INFO}%"
else
    volume=$(osascript -e 'output volume of (get volume settings)' 2>/dev/null)
    sketchybar --set "$NAME" icon="$icon" label="${volume}%"
fi
