#!/usr/bin/env bash
# ABOUTME: SketchyBar plugin triggered on Aerospace workspace change events.
# ABOUTME: Delegates to ws-sync to refresh workspace item state.

REPO_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
"$REPO_DIR/bin/ws-sync"
