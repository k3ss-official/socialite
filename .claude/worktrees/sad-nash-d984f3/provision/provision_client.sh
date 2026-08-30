#!/usr/bin/env bash
# Orchestrator: deploy the latest built site for a lead + create their mailbox.
#
#   provision_client.sh --lead-id ID [--domain NAME] [--vps USER@HOST]
#                       [--email ADDR] [--mail-user LOCALPART] [--dry-run] [--mock DIR]
set -euo pipefail

LEAD="" DOMAIN="" VPS="" EMAIL="admin@example.com" MAIL_USER="info"
PASS_FLAGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lead-id) LEAD="$2"; shift 2 ;;
    --domain) DOMAIN="$2"; shift 2 ;;
    --vps) VPS="$2"; shift 2 ;;
    --email) EMAIL="$2"; shift 2 ;;
    --mail-user) MAIL_USER="$2"; shift 2 ;;
    --dry-run) PASS_FLAGS+=(--dry-run); shift ;;
    --mock) PASS_FLAGS+=(--mock "$2"); shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$LEAD" ]] || { echo "usage: --lead-id ID required" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SITE_BASE="$REPO_ROOT/data/leads/$LEAD/site"

[[ -d "$SITE_BASE" ]] || { echo "no built site for lead '$LEAD' (run the build stage first)" >&2; exit 2; }
LATEST="$(ls -d "$SITE_BASE"/v* 2>/dev/null | sed 's/.*\/v//' | sort -n | tail -1)"
[[ -n "$LATEST" ]] || { echo "no site versions under $SITE_BASE" >&2; exit 2; }
SITE_DIR="$SITE_BASE/v$LATEST"

# placeholder domain until the client's real one is registered
[[ -n "$DOMAIN" ]] || DOMAIN="$LEAD.example"

VPS_FLAGS=()
[[ -n "$VPS" ]] && VPS_FLAGS=(--vps "$VPS")

echo "=== provisioning lead=$LEAD site=v$LATEST domain=$DOMAIN"
"$SCRIPT_DIR/deploy_site.sh" --site "$SITE_DIR" --domain "$DOMAIN" --email "$EMAIL" \
  "${VPS_FLAGS[@]+"${VPS_FLAGS[@]}"}" "${PASS_FLAGS[@]+"${PASS_FLAGS[@]}"}"
"$SCRIPT_DIR/create_mailbox.sh" --domain "$DOMAIN" --user "$MAIL_USER" \
  "${VPS_FLAGS[@]+"${VPS_FLAGS[@]}"}" "${PASS_FLAGS[@]+"${PASS_FLAGS[@]}"}"
echo "=== provisioning complete: https://$DOMAIN"
