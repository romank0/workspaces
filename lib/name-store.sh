# ABOUTME: Shared functions for the workspace display name store.
# ABOUTME: Provides save/read operations on the flat-file name store (SLOT=NAME lines).

NAME_STORE="${NAME_STORE:-$HOME/.local/state/workspaces/names}"

save_display_name() {
    local slot="$1"
    local name="$2"
    mkdir -p "$(dirname "$NAME_STORE")"

    if [[ -f "$NAME_STORE" ]]; then
        grep -v "^${slot}=" "$NAME_STORE" > "$NAME_STORE.tmp" 2>/dev/null || true
        mv "$NAME_STORE.tmp" "$NAME_STORE"
    fi
    echo "${slot}=${name}" >> "$NAME_STORE"
}
