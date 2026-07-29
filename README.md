# Workspaces

Workspace-centric macOS environment using Aerospace, SketchyBar, and iTerm2. Treats workspaces as project contexts rather than collections of unrelated windows.

## How It Works

**Aerospace** manages windows in accordion (stacked) layout — one app visible at a time per workspace, switched with `rcmd-j`/`rcmd-k`.

**SketchyBar** displays active workspaces in a transparent top bar. Only workspaces with windows are shown. Each workspace shows its slot (1-9, A-Z) and display name.

**Templates** define which apps to launch for a given project type. Multiple workspaces can be created from the same template.

**Slots** are the fixed Aerospace workspace identifiers (1-9, A-Z). Each slot has a permanent keybinding (`rcmd-1` through `rcmd-9`, `rcmd-a` through `rcmd-z`). Workspace 1 is persistent and always available as the default workspace.

## Keybindings

All Aerospace shortcuts use a hyper prefix — `alt-cmd-ctrl-` (⌥⌃⌘) in the generated config. Holding three modifiers is awkward, so a Karabiner-Elements rule remaps **Right Command** to that prefix. With the rule installed, press **Right Command** (written `rcmd-` below) plus the key. See [Karabiner-Elements setup](#karabiner-elements) for the rule.

| Key | Action |
|-----|--------|
| `rcmd-enter` | Open workspace picker (switch or create) |
| `rcmd-1`..`rcmd-9` | Switch to workspace slot 1-9 |
| `rcmd-a`..`rcmd-z` | Switch to workspace slot A-Z |
| `rcmd-j` / `rcmd-k` | Focus next/previous window in stack |
| `rcmd-h` / `rcmd-l` | Focus left/right |
| `rcmd-shift-1`..`rcmd-shift-z` | Move window to workspace slot |
| `rcmd-shift-tab` | Move workspace to next monitor |
| `rcmd-tab` | Switch to previous workspace |
| `rcmd-slash` | Switch to tiles layout |
| `rcmd-comma` | Switch to accordion layout |

## Workspace Picker (`rcmd-enter`)

Opens an fzf-based menu in an iTerm2 popup window:

```
Switch or create workspace
  1  Backend
* 2  (current)
  A  AI
─────────────────
  +  New from AI
  +  New from Backend
```

- Select an active workspace to switch to it
- Select a template to create a new workspace (prompts for slot and name)
- Type a slot character for instant filtering (`--select-1`)
- `*` marks the currently focused workspace

## Templates

Defined in `templates/workspaces.yaml`. Each template lists apps to launch:

```yaml
AI:
  apps:
    - app: iTerm
    - app: Google Chrome
      args: ["--new-window", "https://claude.ai"]
```

Apps can be a bare string (just the name) or an object with `app` and `args` for launch arguments.

### Creating a workspace

Via picker: `rcmd-enter` → select template → enter slot and name.

Via command line:

```bash
bin/ws-launch AI A           # Template "AI" in slot A, display name "AI"
bin/ws-launch AI B my-project # Template "AI" in slot B, display name "my-project"
```

## Architecture

```
rcmd-enter → ws-pick-wrapper (background process)
               ├── launches iTerm2 with "Workspace Picker" profile
               ├── ws-pick shows fzf, writes selection to temp file
               └── wrapper reads result, runs aerospace workspace switch

Aerospace workspace change → exec-on-workspace-change hook
               └── sketchybar --trigger aerospace_workspace_change
                      └── ws_trigger item runs ws-sync
                             └── recreates ws.* items in SketchyBar
```

### Display Names

Slot-to-name mappings stored in `~/.local/state/workspaces/names`:

```
A=AI
B=my-project
1=Backend
```

Written by `ws-launch`, read by `ws-sync` for SketchyBar display.

### Aerospace Config Generation

The Aerospace config is not stored in the repo. `bin/generate-aerospace-config.py` reads the default config from `/Applications/AeroSpace.app/Contents/Resources/default-config.toml` and applies:

- Accordion as default layout
- `exec-on-workspace-change` hook for SketchyBar
- `after-startup-command` to run initial ws-sync
- `persistent-workspaces = ["1", "2"]`
- `alt-cmd-ctrl-enter` keybinding for the picker
- Remaps every `alt-` binding to the `alt-cmd-ctrl-` hyper prefix (see [Karabiner-Elements](#karabiner-elements))
- Top gap for SketchyBar bar

This keeps the config up to date with Aerospace releases.

## Project Structure

```
bin/
  setup                      # Install: venv, configs, profiles, services
  generate-aerospace-config.py  # Reads default config, applies modifications
  ws-sync                    # Syncs Aerospace state → SketchyBar items
  ws-launch                  # Launches workspace from template into a slot
  ws-pick                    # fzf picker (runs inside iTerm2)
  ws-pick-wrapper            # Launches picker, acts on result (runs outside iTerm2)
config/
  sketchybar/
    sketchybarrc             # Bar appearance, events, system indicators
    plugins/
      workspaces.sh          # Triggers ws-sync on workspace change
      clock.sh               # Clock display
      battery.sh             # Battery indicator
      volume.sh              # Volume indicator
  iterm2/
    workspace-picker.json    # iTerm2 dynamic profile for picker popup
templates/
  workspaces.yaml            # Workspace template definitions
```

## Setup

### Dependencies

Install via Homebrew:

```bash
brew install --cask aerospace
brew install sketchybar jq yq fzf
```

iTerm2 and Python 3.11+ are also required.

### Install

```bash
bin/setup
```

This will:

1. Check all dependencies are installed
2. Create a Python venv and install `tomli_w` (for TOML config generation)
3. Warn if "Automatically rearrange Spaces" is enabled in macOS settings
4. Back up existing Aerospace and SketchyBar configs
5. Generate Aerospace config from the app's default
6. Symlink SketchyBar config from this repo
7. Install iTerm2 dynamic profile for the workspace picker
8. Start or reload Aerospace and SketchyBar

Safe to run multiple times.

### Karabiner-Elements

Aerospace shortcuts use the `alt-cmd-ctrl-` hyper prefix. Install [Karabiner-Elements](https://karabiner-elements.pqrs.org/) and add this rule under a profile's `complex_modifications.rules` (in `~/.config/karabiner/karabiner.json`) so **Right Command** produces that prefix on its own:

```json
{
    "description": "Right Command to Cmd+Ctrl+Opt (For AeroSpace)",
    "manipulators": [
        {
            "from": {
                "key_code": "right_command",
                "modifiers": { "optional": ["any"] }
            },
            "to": [
                {
                    "key_code": "left_command",
                    "modifiers": ["left_control", "left_option"]
                }
            ],
            "type": "basic"
        }
    ]
}
```

With the rule active, hold **Right Command** in place of the `alt-cmd-ctrl-` prefix — e.g. Right Command + `j` runs `alt-cmd-ctrl-j`.

## Future Work

- Notification badges per workspace (phase 2)
- Per-workspace app filtering
- Persistent workspace state across restarts
