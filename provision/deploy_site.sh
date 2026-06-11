#!/usr/bin/env bash
# Deploy a built static site bundle to the VPS: rsync + nginx vhost + SSL.
# Idempotent: safe to re-run; converges instead of erroring.
#
#   deploy_site.sh --site DIR --domain NAME [--vps USER@HOST] [--webroot BASE]
#                  [--email ADDR] [--dry-run] [--mock DIR]
#
# Modes: real (default, needs --vps) | --dry-run (print, do nothing)
#        | --mock DIR (simulate the VPS filesystem under DIR; remote commands logged)
set -euo pipefail

SITE="" DOMAIN="" VPS="" WEBROOT="/var/www" EMAIL="admin@example.com"
DRY=0 MOCK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site) SITE="$2"; shift 2 ;;
    --domain) DOMAIN="$2"; shift 2 ;;
    --vps) VPS="$2"; shift 2 ;;
    --webroot) WEBROOT="$2"; shift 2 ;;
    --email) EMAIL="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --mock) MOCK="$2"; shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$SITE" && -n "$DOMAIN" ]] || { echo "usage: --site DIR --domain NAME required" >&2; exit 2; }
[[ -d "$SITE" ]] || { echo "site dir not found: $SITE" >&2; exit 2; }
[[ $DRY -eq 1 || -n "$MOCK" || -n "$VPS" ]] || { echo "need --vps for a real deploy (or --dry-run/--mock)" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TPL="$SCRIPT_DIR/templates/nginx-site.conf.tpl"
DOCROOT="$WEBROOT/$DOMAIN"
CONF_AVAIL="/etc/nginx/sites-available/$DOMAIN.conf"
CONF_ENABLED="/etc/nginx/sites-enabled/$DOMAIN.conf"

# remote: run a command on the target (ssh in real mode, log in mock, print in dry)
remote() {
  if [[ $DRY -eq 1 ]]; then echo "DRY-RUN: ssh \"${VPS:-<your-vps>}\" -- $*"
  elif [[ -n "$MOCK" ]]; then echo "ssh: $*" >> "$MOCK/commands.log"; echo "MOCK: $*"
  else ssh "$VPS" -- "$@"; fi
}

# push_files SRC DEST: rsync in real mode, cp into the fake root in mock
push_files() {
  if [[ $DRY -eq 1 ]]; then echo "DRY-RUN: rsync -az --delete \"$1/\" \"${VPS:-<your-vps>}:$2/\""
  elif [[ -n "$MOCK" ]]; then
    mkdir -p "$MOCK$2"; cp -R "$1/." "$MOCK$2/"
    echo "rsync: $1/ -> $2/" >> "$MOCK/commands.log"; echo "MOCK: rsync $1/ -> $2/"
  else rsync -az --delete "$1/" "$VPS:$2/"; fi
}

# install_content DEST: write stdin to a file on the target
install_content() {
  local content; content="$(cat)"
  if [[ $DRY -eq 1 ]]; then echo "DRY-RUN: write $1 <<EOF"; echo "$content"; echo "EOF"
  elif [[ -n "$MOCK" ]]; then
    mkdir -p "$MOCK$(dirname "$1")"; printf '%s\n' "$content" > "$MOCK$1"
    echo "write: $1" >> "$MOCK/commands.log"; echo "MOCK: wrote $1"
  else printf '%s\n' "$content" | ssh "$VPS" -- "cat > '$1'"; fi
}

[[ -n "$MOCK" ]] && mkdir -p "$MOCK"

echo "== deploy $DOMAIN (site: $SITE)"
push_files "$SITE" "$DOCROOT"

DOMAIN="$DOMAIN" ROOT="$DOCROOT" envsubst '${DOMAIN} ${ROOT}' < "$TPL" | install_content "$CONF_AVAIL"
remote ln -sf "$CONF_AVAIL" "$CONF_ENABLED"
remote nginx -t
remote systemctl reload nginx

# certbot is idempotent-ish but slow; skip when the cert already exists
if [[ $DRY -eq 1 || -n "$MOCK" ]]; then
  remote certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL"
else
  if ssh "$VPS" -- "test -d /etc/letsencrypt/live/$DOMAIN"; then
    echo "== cert exists for $DOMAIN, skipping certbot"
  else
    remote certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL"
  fi
fi
echo "== done: $DOMAIN"
