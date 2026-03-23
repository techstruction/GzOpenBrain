#!/usr/bin/env bash
# ============================================================================
# nemoclaw-sync.sh — NemoClaw Backup & Sync Utility
# ============================================================================
# Syncs all irreplaceable NemoClaw data between the K3s Sandbox container
# and the Host OS, and creates timestamped backup snapshots.
#
# Architecture:
#   K3s Sandbox container (/sandbox/.openclaw/) is mounted via hostPath to
#   /home/tonyg/GzOpenBrain/open-claw/ on the Host OS. Most files are already
#   shared, but some (like auth-profiles.json created by openclaw onboard)
#   may only exist inside the container. This script pulls those files out
#   and creates compressed backups of everything irreplaceable.
#
# Usage:
#   ./nemoclaw-sync.sh              # Full sync + backup
#   ./nemoclaw-sync.sh --backup     # Backup only (no container pull)
#   ./nemoclaw-sync.sh --pull       # Pull from container only (no backup)
#   ./nemoclaw-sync.sh --push       # Push local changes into the container
#   ./nemoclaw-sync.sh --status     # Show what would be synced
#
# Requires: kubectl access via openshell doctor exec
# ============================================================================

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────
HOST_OPENCLAW="/home/tonyg/GzOpenBrain/open-claw"
BACKUP_DIR="/home/tonyg/GzOpenBrain/.nemoclaw-backups"
POD_NAME="nemoclaw"
POD_NAMESPACE="openshell"
KUBECTL="$HOME/.local/bin/openshell doctor exec -- kubectl"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ── Colors ─────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log()   { echo -e "${GREEN}[SYNC]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }

# ── Preflight ──────────────────────────────────────────────────────────────
check_pod() {
    if ! $KUBECTL get pod "$POD_NAME" -n "$POD_NAMESPACE" > /dev/null 2>&1; then
        error "Pod '$POD_NAME' not found in namespace '$POD_NAMESPACE'."
        error "Is the NemoClaw sandbox running? Try: openshell sandbox list"
        exit 1
    fi
    log "Pod '$POD_NAME' is running."
}

# ── Irreplaceable Data Paths (relative to /sandbox/.openclaw/) ─────────────
SYNC_DIRS=(
    "agents/main/memory"
    "agents/main/sessions"
    "agents/main/agent"
    "skills"
    "workspace/skills"
    "workspace/.openclaw"
)

SYNC_FILES=(
    "openclaw.json"
    "openclaw.json.bak"
    "update-check.json"
    "agents/main/AGENTS.md"
    "workspace/IDENTITY.md"
    "workspace/USER.md"
    "workspace/SOUL.md"
    "workspace/TOOLS.md"
    "workspace/HEARTBEAT.md"
    "workspace/BOOTSTRAP.md"
)

# ── Pull: Container → Host ────────────────────────────────────────────────
pull_from_container() {
    log "Pulling irreplaceable data from container → host..."
    local pulled=0
    local skipped=0

    # Pull directories via tar
    for dir in "${SYNC_DIRS[@]}"; do
        if $KUBECTL exec "$POD_NAME" -n "$POD_NAMESPACE" -- test -d "/sandbox/.openclaw/$dir" 2>/dev/null; then
            mkdir -p "$HOST_OPENCLAW/$dir"
            $KUBECTL exec "$POD_NAME" -n "$POD_NAMESPACE" -- \
                tar cf - -C /sandbox/.openclaw "$dir" 2>/dev/null | \
                tar xf - -C "$HOST_OPENCLAW" 2>/dev/null
            local fcount=$(find "$HOST_OPENCLAW/$dir" -type f 2>/dev/null | wc -l)
            info "  ✓ $dir/ ($fcount files)"
            pulled=$((pulled + 1))
        else
            info "  - $dir/ (not in container)"
            skipped=$((skipped + 1))
        fi
    done

    # Pull individual files
    for file in "${SYNC_FILES[@]}"; do
        if $KUBECTL exec "$POD_NAME" -n "$POD_NAMESPACE" -- test -f "/sandbox/.openclaw/$file" 2>/dev/null; then
            mkdir -p "$(dirname "$HOST_OPENCLAW/$file")"
            $KUBECTL exec "$POD_NAME" -n "$POD_NAMESPACE" -- \
                cat "/sandbox/.openclaw/$file" > "$HOST_OPENCLAW/$file" 2>/dev/null
            info "  ✓ $file"
            pulled=$((pulled + 1))
        else
            info "  - $file (not in container)"
            skipped=$((skipped + 1))
        fi
    done

    # Also pull any *.md files at the root level
    for md in $($KUBECTL exec "$POD_NAME" -n "$POD_NAMESPACE" -- find /sandbox/.openclaw -maxdepth 1 -name '*.md' -printf '%f\n' 2>/dev/null); do
        $KUBECTL exec "$POD_NAME" -n "$POD_NAMESPACE" -- \
            cat "/sandbox/.openclaw/$md" > "$HOST_OPENCLAW/$md" 2>/dev/null
        info "  ✓ $md (root .md)"
        pulled=$((pulled + 1))
    done

    log "Pull complete: $pulled synced, $skipped skipped."
}

# ── Push: Host → Container ────────────────────────────────────────────────
push_to_container() {
    log "Pushing local changes from host → container..."
    local pushed=0

    # Push directories via tar
    for dir in "${SYNC_DIRS[@]}"; do
        if [[ -d "$HOST_OPENCLAW/$dir" ]]; then
            tar cf - -C "$HOST_OPENCLAW" "$dir" 2>/dev/null | \
                $KUBECTL exec -i "$POD_NAME" -n "$POD_NAMESPACE" -- \
                tar xf - -C /sandbox/.openclaw 2>/dev/null
            info "  ✓ $dir/"
            pushed=$((pushed + 1))
        fi
    done

    # Push individual files
    for file in "${SYNC_FILES[@]}"; do
        if [[ -f "$HOST_OPENCLAW/$file" ]]; then
            cat "$HOST_OPENCLAW/$file" | \
                $KUBECTL exec -i "$POD_NAME" -n "$POD_NAMESPACE" -- \
                sh -c "cat > /sandbox/.openclaw/$file" 2>/dev/null
            info "  ✓ $file"
            pushed=$((pushed + 1))
        fi
    done

    log "Push complete: $pushed items updated in container."
    warn "Restart the gateway daemon for config changes to take effect:"
    warn "  kubectl exec nemoclaw -n openshell -- pkill -f openclaw"
}

# ── Backup: Timestamped Snapshot ──────────────────────────────────────────
create_backup() {
    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/nemoclaw-backup-$TIMESTAMP.tar.gz"

    log "Creating backup snapshot: $backup_file"

    # Build list of existing paths to archive
    local paths_to_backup=()
    for dir in "${SYNC_DIRS[@]}"; do
        [[ -d "$HOST_OPENCLAW/$dir" ]] && paths_to_backup+=("$dir")
    done
    for file in "${SYNC_FILES[@]}"; do
        [[ -f "$HOST_OPENCLAW/$file" ]] && paths_to_backup+=("$file")
    done

    if [[ ${#paths_to_backup[@]} -eq 0 ]]; then
        warn "No data found to backup!"
        return 1
    fi

    tar czf "$backup_file" \
        -C "$HOST_OPENCLAW" \
        "${paths_to_backup[@]}" \
        2>/dev/null || true

    local size=$(du -sh "$backup_file" 2>/dev/null | cut -f1)
    log "Backup complete: $backup_file ($size)"

    # Prune old backups, keep last 10
    local count=$(ls -1 "$BACKUP_DIR"/nemoclaw-backup-*.tar.gz 2>/dev/null | wc -l)
    if (( count > 10 )); then
        local to_delete=$((count - 10))
        ls -1t "$BACKUP_DIR"/nemoclaw-backup-*.tar.gz | tail -n "$to_delete" | xargs rm -f
        log "Pruned $to_delete old backup(s). Keeping last 10."
    fi
}

# ── Status: Show what exists ──────────────────────────────────────────────
show_status() {
    info "NemoClaw Sync Status"
    info "===================="
    info "Host path:    $HOST_OPENCLAW"
    info "Backup dir:   $BACKUP_DIR"
    info "Pod:          $POD_NAME ($POD_NAMESPACE)"
    echo ""

    info "Directories:"
    for dir in "${SYNC_DIRS[@]}"; do
        if [[ -d "$HOST_OPENCLAW/$dir" ]]; then
            local fcount=$(find "$HOST_OPENCLAW/$dir" -type f 2>/dev/null | wc -l)
            info "  ✓ $dir/ ($fcount files)"
        else
            warn "  ✗ $dir/ (MISSING)"
        fi
    done

    echo ""
    info "Files:"
    for file in "${SYNC_FILES[@]}"; do
        if [[ -f "$HOST_OPENCLAW/$file" ]]; then
            local fsize=$(du -sh "$HOST_OPENCLAW/$file" 2>/dev/null | cut -f1)
            info "  ✓ $file ($fsize)"
        else
            warn "  ✗ $file (MISSING)"
        fi
    done

    echo ""
    info "Existing backups:"
    if ls "$BACKUP_DIR"/nemoclaw-backup-*.tar.gz > /dev/null 2>&1; then
        ls -1th "$BACKUP_DIR"/nemoclaw-backup-*.tar.gz | head -5 | while read f; do
            local fsize=$(du -sh "$f" 2>/dev/null | cut -f1)
            info "  📦 $(basename "$f") ($fsize)"
        done
        local total=$(ls -1 "$BACKUP_DIR"/nemoclaw-backup-*.tar.gz 2>/dev/null | wc -l)
        (( total > 5 )) && info "  ... and $((total - 5)) more"
    else
        warn "  No backups found."
    fi
}

# ── Main ──────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "  NemoClaw Sync & Backup Utility"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════"
    echo ""

    case "${1:-}" in
        --backup)
            create_backup
            ;;
        --pull)
            check_pod
            pull_from_container
            ;;
        --push)
            check_pod
            push_to_container
            ;;
        --status)
            show_status
            ;;
        *)
            # Full sync: pull from container, then backup
            check_pod
            pull_from_container
            echo ""
            create_backup
            echo ""
            show_status
            ;;
    esac

    echo ""
    log "Done."
}

main "$@"
