# Workspace Display

## Purpose

Display name storage and SketchyBar workspace item synchronization.

## Requirements

### Requirement: Display name store format
The system SHALL persist workspace display names in `~/.local/state/workspaces/names` as a flat file with `SLOT=NAME` lines, one per slot.

#### Scenario: Save and read back
- **WHEN** a display name "DevEnv" is saved for slot D
- **THEN** reading the name store returns "DevEnv" for slot D

#### Scenario: Multiple names coexist
- **WHEN** names are saved for slots A, B, and C
- **THEN** all three names can be read back independently

### Requirement: SketchyBar occupied workspaces
ws-sync SHALL create a SketchyBar item for each workspace that has at least one window or is currently focused.

#### Scenario: Occupied workspace shown
- **GIVEN** workspace A has windows
- **WHEN** ws-sync runs
- **THEN** SketchyBar has an item named `ws.A`

#### Scenario: Empty unfocused workspace hidden
- **GIVEN** workspace B has no windows and is not focused
- **WHEN** ws-sync runs
- **THEN** SketchyBar has no item named `ws.B`

### Requirement: SketchyBar focused highlight
ws-sync SHALL style the focused workspace item differently from occupied-but-unfocused items.

#### Scenario: Focused workspace color
- **GIVEN** workspace A is focused
- **WHEN** ws-sync runs
- **THEN** item `ws.A` has icon color `0xffe0af68` (gold)

#### Scenario: Unfocused workspace color
- **GIVEN** workspace B has windows but is not focused
- **WHEN** ws-sync runs
- **THEN** item `ws.B` has icon color `0xffcdd6f4` (lavender)

### Requirement: SketchyBar display names
ws-sync SHALL show the display name from the name store as the item label. If no name is stored, the label SHALL be empty.

#### Scenario: Named workspace label
- **GIVEN** slot A has display name "AI" in the name store
- **AND** workspace A has windows
- **WHEN** ws-sync runs
- **THEN** item `ws.A` has label "AI"

#### Scenario: Unnamed workspace label
- **GIVEN** slot 1 has no display name in the name store
- **AND** workspace 1 has windows
- **WHEN** ws-sync runs
- **THEN** item `ws.1` has an empty label

### Requirement: SketchyBar click-to-switch
Each workspace item in SketchyBar SHALL switch to that workspace when clicked.

#### Scenario: Click switches workspace
- **GIVEN** SketchyBar has item `ws.A`
- **WHEN** the item's click script executes
- **THEN** it runs `aerospace workspace A`
