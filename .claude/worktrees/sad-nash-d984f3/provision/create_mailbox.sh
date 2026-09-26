#!/usr/bin/env bash
# One branded mailbox per client on the VPS's docker-mailserver.
#
#   create_mailbox.sh --domain NAME [--user LOCALPART] [--vps USER@HOST]
#                     [--password PASS] [--dry-run] [--mock DIR]
#
# Different mail stack? Swap the two `docker exec mailserver setup email ...`
# lines: mailcow has an API (curl), stalwart has `stalwart-cli account create`.
# Idempotent: skips creation if the address already exists.
# The generated password is printed ONCE to stdout and never written to logs.
set -euo pipefail

DOMAIN="" USER_PART="info" VPS="" PASSWORD="" DRY=0 MOCK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) DOMAIN="$2"; shift 2 ;;
    --user) USER_PART="$2"; shift 2 ;;
    --vps) VPS="$2"; shift 2 ;;
    --password) PASSWORD="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --mock) MOCK="$2"; shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$DOMAIN" ]] || { echo "usage: --domain NAME required" >&2; exit 2; }
[[ $DRY -eq 1 || -n "$MOCK" || -n "$VPS" ]] || { echo "need --vps (or --dry-run/--mock)" >&2; exit 2; }

ADDR="$USER_PART@$DOMAIN"
# openssl rand: finite output, no SIGPIPE under pipefail (urandom|head trips exit 141)
[[ -n "$PASSWORD" ]] || PASSWORD="$(openssl rand -hex 12)"

remote() {
  if [[ $DRY -eq 1 ]]; then echo "DRY-RUN: ssh \"${VPS:-<your-vps>}\" -- $*"
  elif [[ -n "$MOCK" ]]; then mkdir -p "$MOCK"; echo "ssh: $*" >> "$MOCK/commands.log"; echo "MOCK: $*"
  else ssh "$VPS" -- "$@"; fi
}

echo "== mailbox $ADDR"
if [[ $DRY -eq 0 && -z "$MOCK" ]]; then
  if ssh "$VPS" -- "docker exec mailserver setup email list" | grep -qF "$ADDR"; then
    echo "== $ADDR already exists, skipping"
    exit 0
  fi
fi

# password passed via stdin so it never appears in ssh argv or any log
if [[ $DRY -eq 1 ]]; then
  echo "DRY-RUN: ssh \"${VPS:-<your-vps>}\" -- docker exec -i mailserver setup email add \"$ADDR\" '<password from stdin>'"
elif [[ -n "$MOCK" ]]; then
  echo "ssh: docker exec -i mailserver setup email add $ADDR <password-redacted>" >> "$MOCK/commands.log"
  echo "MOCK: mailbox add $ADDR"
else
  printf '%s' "$PASSWORD" | ssh "$VPS" -- "docker exec -i mailserver setup email add '$ADDR'"
fi

cat <<BANNER
==============================================================
  MAILBOX CREDENTIALS — record now, shown once, never logged
  address:  $ADDR
  password: $PASSWORD
==============================================================
BANNER
