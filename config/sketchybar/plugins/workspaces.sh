#!/usr/bin/env bash
# ABOUTME: SketchyBar plugin triggered on Aerospace workspace change events.
# ABOUTME: Delegates to ws-sync to refresh workspace item state.

REAL_SCRIPT_DIR="$(cd -P "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$REAL_SCRIPT_DIR/../../.." && pwd)"
"$REPO_DIR/bin/ws-sync"
