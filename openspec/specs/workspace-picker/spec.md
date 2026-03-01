# Workspace Picker

## Purpose

Interactive overlay for switching between workspaces and creating new ones from templates, using choose-gui.

## Requirements

### Requirement: Active workspace listing
The picker SHALL display all workspaces that have at least one window, showing the slot identifier and display name.

#### Scenario: Multiple active workspaces
- **GIVEN** workspaces 1 and A have windows
- **AND** slot A has display name "MyWork" in the name store
- **WHEN** ws-pick builds its entry list
- **THEN** entries include workspace 1 and workspace A
- **AND** workspace A's entry shows "MyWork" as its label

#### Scenario: Empty workspaces excluded
- **GIVEN** workspace B has no windows and is not focused
- **WHEN** ws-pick builds its entry list
- **THEN** no entry for workspace B appears

### Requirement: Focused workspace marker
The picker SHALL mark the currently focused workspace with a `*` prefix to distinguish it from other entries.

#### Scenario: Focused workspace highlighted
- **GIVEN** workspace A is the focused workspace
- **AND** workspaces 1 and A both have windows
- **WHEN** ws-pick builds its entry list
- **THEN** workspace A's entry starts with `*`
- **AND** workspace 1's entry starts with ` ` (space)

### Requirement: Template listing
The picker SHALL list available templates from `templates/workspaces.yaml` as creation options, formatted as `+ New from <template>`.

#### Scenario: Templates shown
- **GIVEN** `templates/workspaces.yaml` contains templates "Dev" and "Ops"
- **WHEN** ws-pick builds its entry list
- **THEN** entries include `+ New from Dev` and `+ New from Ops`

### Requirement: Switch workspace
Selecting an active workspace entry SHALL switch Aerospace's focused workspace to that slot.

#### Scenario: Switch to workspace
- **GIVEN** workspace A exists with windows
- **AND** the current focused workspace is 1
- **WHEN** the user selects workspace A in the picker
- **THEN** Aerospace's focused workspace becomes A

### Requirement: Create workspace flow
Selecting a template entry SHALL prompt for slot selection (from available slots) and workspace name, then launch the workspace via ws-launch.

#### Scenario: Create from template
- **GIVEN** `templates/workspaces.yaml` contains template "Dev" with app iTerm
- **AND** slots 2-9 and A-Z are available
- **WHEN** the user selects `+ New from Dev`
- **AND** picks slot B and enters name "Backend"
- **THEN** `ws-launch Dev B Backend` runs
- **AND** workspace B is created with the template's apps

### Requirement: Slot availability
The slot picker SHALL only show slots that have no windows assigned, preventing conflicts with existing workspaces.

#### Scenario: Used slots excluded
- **GIVEN** workspaces 1 and A have windows
- **WHEN** the slot picker displays available slots
- **THEN** slot 1 and slot A are NOT listed
- **AND** other slots (2-9, B-Z) are listed
