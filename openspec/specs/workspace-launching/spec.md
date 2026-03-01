# Workspace Launching

## Purpose

Creates workspaces from YAML templates by launching apps and placing their windows on the target Aerospace workspace slot.

## Requirements

### Requirement: Launch apps from template
The system SHALL read a named template from `templates/workspaces.yaml` and launch each listed app, placing all new windows on the specified workspace slot.

#### Scenario: Basic template launch
- **GIVEN** `templates/workspaces.yaml` contains a template "Test" with apps iTerm and Google Chrome
- **WHEN** `ws-launch Test T TestWs` runs
- **THEN** workspace T contains windows for both iTerm2 and Google Chrome
- **AND** Aerospace's focused workspace is T

#### Scenario: Template not found
- **WHEN** `ws-launch NonExistent T Test` runs
- **THEN** the command exits with a non-zero exit code

### Requirement: No window stealing
The system SHALL NOT move existing windows from other workspaces when launching a new workspace. Only newly created windows SHALL be placed on the target slot.

#### Scenario: Existing windows preserved
- **GIVEN** `templates/workspaces.yaml` contains a template "BrowserTest" with app Google Chrome with args `["--new-window", "https://example.com"]`
- **AND** workspace A has a Google Chrome window with a known window ID
- **WHEN** `ws-launch BrowserTest B TestB` runs
- **THEN** workspace A still contains the original Chrome window ID
- **AND** workspace B has a different Chrome window ID

### Requirement: Display name persistence
The system SHALL store the display name for a workspace slot in `~/.local/state/workspaces/names` as `SLOT=NAME` entries.

#### Scenario: Name saved on launch
- **GIVEN** `templates/workspaces.yaml` contains a template "Minimal" with app iTerm
- **WHEN** `ws-launch Minimal T MyWorkspace` runs
- **THEN** file `~/.local/state/workspaces/names` contains line `T=MyWorkspace`

#### Scenario: Name overwritten on relaunch
- **GIVEN** slot T has name "OldName" in the name store
- **AND** `templates/workspaces.yaml` contains a template "Minimal" with app iTerm
- **WHEN** `ws-launch Minimal T NewName` runs
- **THEN** the name store contains `T=NewName`
- **AND** the name store does NOT contain `T=OldName`

### Requirement: Browser URL support
The system SHALL detect URL arguments in template app entries and open a new browser window navigated to that URL, without spawning a separate app instance.

#### Scenario: Chrome window with URL
- **GIVEN** `templates/workspaces.yaml` contains a template "Web" with app Google Chrome and args `["--new-window", "https://example.com"]`
- **WHEN** `ws-launch Web T TestWeb` runs
- **THEN** a new Google Chrome window is created on workspace T
- **AND** the active tab URL contains "example.com"

### Requirement: iTerm profile selection
The system SHALL support a `profile-tag` field on template app entries. When present, it queries iTerm2 profiles matching that tag and lets the user select one before launching. The "Default" profile SHALL always be available as an option.

#### Scenario: Multiple profiles with tag
- **GIVEN** iTerm2 has profiles "ws1" and "ws2" both tagged "test-tag"
- **AND** `templates/workspaces.yaml` contains a template "Profile" with app iTerm and `profile-tag: test-tag`
- **WHEN** `ws-launch Profile T TestProf` runs
- **THEN** a choose-gui picker appears listing "Default", "ws1", and "ws2"
- **AND** the selected profile is used to create the iTerm window

#### Scenario: Single profile with tag
- **GIVEN** iTerm2 has exactly one profile tagged "solo-tag"
- **AND** `templates/workspaces.yaml` contains a template "Solo" with app iTerm and `profile-tag: solo-tag`
- **WHEN** `ws-launch Solo T TestSolo` runs
- **THEN** a choose-gui picker appears listing "Default" and the tagged profile

#### Scenario: Default profile always available
- **GIVEN** no iTerm2 profiles are tagged "nonexistent-tag"
- **AND** `templates/workspaces.yaml` contains a template "Fallback" with app iTerm and `profile-tag: nonexistent-tag`
- **WHEN** `ws-launch Fallback T TestFallback` runs
- **THEN** the "Default" profile is used automatically

### Requirement: Bare string app entries
The system SHALL support apps specified as bare strings (just the app name) in templates, launching them with a new window and no arguments.

#### Scenario: Bare string app
- **GIVEN** `templates/workspaces.yaml` contains a template "Simple" with `- iTerm` as a bare string entry
- **WHEN** `ws-launch Simple T TestSimple` runs
- **THEN** an iTerm2 window is created on workspace T

### Requirement: Single app instance
The system SHALL create new windows within existing app instances rather than spawning separate processes, to avoid duplicate dock icons.

#### Scenario: No duplicate dock processes
- **GIVEN** Google Chrome is already running
- **AND** `templates/workspaces.yaml` contains a template "Browser" with app Google Chrome and args `["--new-window", "https://example.com"]`
- **WHEN** `ws-launch Browser T TestBrowser` runs
- **THEN** the number of Chrome processes does not increase
