# Aerospace Config Generation

## Purpose

Generates Aerospace configuration by reading the app's default config and applying workspace-centric modifications.

## Requirements

### Requirement: Derive from default config
The config generator SHALL read the default config from `/Applications/AeroSpace.app/Contents/Resources/default-config.toml` and apply modifications on top of it, preserving all unmodified defaults.

#### Scenario: Default config preserved
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML contains all key-mapping settings from the default config
- **AND** unmodified keybindings from the default config are present

### Requirement: Accordion layout
The generated config SHALL set the default root container layout to accordion with zero padding.

#### Scenario: Accordion settings
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has `default-root-container-layout = "accordion"`
- **AND** `accordion-padding = 0`

### Requirement: SketchyBar gap
The generated config SHALL set a top outer gap to accommodate the SketchyBar bar.

#### Scenario: Top gap for bar
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has `gaps.outer.top = 36`

### Requirement: Workspace change hook
The generated config SHALL trigger a SketchyBar event on workspace changes, passing the focused and previous workspace as environment variables.

#### Scenario: Workspace change event
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has `exec-on-workspace-change` configured to trigger `sketchybar --trigger aerospace_workspace_change` with `FOCUSED` and `PREV` variables

### Requirement: Accordion focus bindings
The generated config SHALL override default focus bindings to cycle left/right through accordion windows with wrap-around.

#### Scenario: Focus left binding
- **WHEN** generate-aerospace-config.py runs
- **THEN** `alt-j` is bound to `focus left --boundaries-action wrap-around-the-workspace`

#### Scenario: Focus right binding
- **WHEN** generate-aerospace-config.py runs
- **THEN** `alt-k` is bound to `focus right --boundaries-action wrap-around-the-workspace`

### Requirement: Picker binding
The generated config SHALL bind a key to launch the workspace picker.

#### Scenario: Picker keybinding
- **WHEN** generate-aerospace-config.py runs
- **THEN** `alt-enter` is bound to `exec-and-forget` followed by the path to `ws-pick`

### Requirement: Floating picker window
The generated config SHALL include an on-window-detected rule that floats windows titled "Workspace Picker".

#### Scenario: Floating rule present
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has an `on-window-detected` entry matching `window-title-regex-substring = "Workspace Picker"` with `run = "layout floating"`

### Requirement: Persistent workspaces
The generated config SHALL keep workspaces "1" and "2" as persistent so they survive config reloads. Workspace "1" SHALL be pinned to the main monitor (the display with the dock) and workspace "2" SHALL be pinned to the secondary monitor.

#### Scenario: Persistent workspaces
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has `persistent-workspaces` containing `"1"` and `"2"`

#### Scenario: Monitor assignment
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has `workspace-to-monitor-force-assignment` mapping `"1"` to `"main"` and `"2"` to `"secondary"`

### Requirement: Startup sync
The generated config SHALL run ws-sync after Aerospace starts to initialize SketchyBar workspace items.

#### Scenario: After-startup command
- **WHEN** generate-aerospace-config.py runs
- **THEN** the output TOML has `after-startup-command` containing `exec-and-forget` with the path to `ws-sync`
