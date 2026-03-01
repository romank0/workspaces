# ABOUTME: Feature specification for integration test scenarios.
# ABOUTME: Each feature has testable scenarios with observable outcomes.

## F1: Workspace Launching (ws-launch)

### F1.1: Basic launch
- Given a template "AI" and an unused slot "T"
- When `ws-launch AI T TestName` runs
- Then workspace T has windows for each app in the AI template
- And `~/.local/state/workspaces/names` contains `T=TestName`
- And Aerospace's focused workspace is T

### F1.2: No window stealing
- Given workspace A has a Chrome window
- When `ws-launch AI B Test` runs
- Then workspace A still has its original Chrome window
- And workspace B has its own new Chrome window
- And the window IDs on A are unchanged

### F1.3: iTerm profile selection
- Given a template app with `profile-tag: monorepo-ws`
- When ws-launch runs
- Then the created iTerm window uses one of the profiles tagged "monorepo-ws"

### F1.4: Browser URL
- Given a template app with args containing a URL
- When ws-launch runs
- Then a new browser window opens with that URL in the active tab

### F1.5: Single dock icon
- When ws-launch creates app windows
- Then no new app instances are spawned (no `-n` flag)
- Observable: window count for the app process stays at 1

## F2: Workspace Picker (ws-pick)

### F2.1: Active workspace listing
- Given workspaces 1 and A have windows
- When ws-pick builds its entry list
- Then entries include both workspaces with display names

### F2.2: Focused workspace marker
- Given workspace A is focused
- When ws-pick builds its entry list
- Then workspace A's entry starts with `*`
- And other entries start with ` `

### F2.3: Template listing
- When ws-pick builds its entry list
- Then entries include `+ New from <template>` for each template in workspaces.yaml

### F2.4: Switch action
- Given workspace A exists with windows
- When the user selects workspace A in the picker
- Then Aerospace's focused workspace becomes A

## F3: Display Name Store

### F3.1: Save and load
- When `ws-launch AI T MyName` runs
- Then file `~/.local/state/workspaces/names` contains line `T=MyName`

### F3.2: Overwrite existing
- Given slot T has name "Old"
- When `ws-launch AI T New` runs
- Then the name store has `T=New` and no `T=Old`

## F4: SketchyBar Sync (ws-sync)

### F4.1: Occupied workspaces shown
- Given workspaces 1 and A have windows
- When ws-sync runs
- Then SketchyBar has items `ws.1` and `ws.A`

### F4.2: Empty workspaces hidden
- Given workspace B has no windows and is not focused
- When ws-sync runs
- Then SketchyBar has no item `ws.B`

### F4.3: Focused workspace highlighted
- Given workspace A is focused
- When ws-sync runs
- Then item `ws.A` has icon color `0xffe0af68` (gold)
- And other ws items have icon color `0xffcdd6f4` (lavender)

### F4.4: Display names shown
- Given slot A has display name "AI"
- When ws-sync runs
- Then item `ws.A` has label "AI"

## F5: Aerospace Config Generation

### F5.1: Accordion layout
- When generate-aerospace-config.py runs
- Then output TOML has `default-root-container-layout = "accordion"`
- And `accordion-padding = 0`

### F5.2: Gaps
- Then output TOML has `gaps.outer.top = 36`

### F5.3: Workspace change hook
- Then output TOML has `exec-on-workspace-change` triggering sketchybar

### F5.4: Keybindings
- Then output TOML has alt-j = focus left with wrap
- And alt-k = focus right with wrap
- And alt-enter = exec-and-forget ws-pick

### F5.5: Floating picker rule
- Then output TOML has on-window-detected rule for "Workspace Picker" → layout floating

### F5.6: Persistent workspace
- Then output TOML has persistent-workspaces = ["1"]

## F6: Window Navigation

### F6.1: Focus cycling
- Given workspace T has windows W1 and W2 in accordion
- When `aerospace focus left` runs
- Then the focused window changes
- When `aerospace focus left` runs again (with wrap)
- Then focus wraps back

## F7: Template Format

### F7.1: Bare string app
- Given template has `- iTerm` (bare string)
- When ws-launch runs
- Then iTerm window is created

### F7.2: App with args
- Given template has `app: Google Chrome` with `args: ["--new-window", "https://example.com"]`
- When ws-launch runs
- Then Chrome window opens with https://example.com

### F7.3: App with profile-tag
- Given template has `app: iTerm` with `profile-tag: monorepo-ws`
- When ws-launch runs
- Then iTerm window uses a profile from that tag group
