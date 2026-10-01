#!/usr/bin/env bash
# Proof harness: exercises deploy + mailbox in --mock and --dry-run modes.
# No network, no real hosts. Exits nonzero on any failure.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAKE="$(mktemp -d /tmp/socialite-test-vps.XXXXXX)"
TMP_SITE="$(mktemp -d /tmp/socialite-test-site.XXXXXX)"
trap 'rm -rf "$FAKE" "$TMP_SITE"' EXIT
PASS=0; FAIL=0

check() { # check <desc> <cmd...>
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "PASS: $desc"; PASS=$((PASS+1));
  else echo "FAIL: $desc"; FAIL=$((FAIL+1)); fi
}

# fresh fake VPS + fake site bundle
printf '<html><body>fake client site</body></html>' > "$TMP_SITE/index.html"
printf 'body{}' > "$TMP_SITE/style.css"

echo "--- mock deploy"
"$SCRIPT_DIR/deploy_site.sh" --site "$TMP_SITE" --domain testclient.example \
  --email ops@example.com --mock "$FAKE"
check "site files landed in fake webroot"      test -f "$FAKE/var/www/testclient.example/index.html"
check "nginx conf rendered"                    test -f "$FAKE/etc/nginx/sites-available/testclient.example.conf"
check "conf has right server_name"             grep -q "server_name testclient.example;" "$FAKE/etc/nginx/sites-available/testclient.example.conf"
check "symlink command logged"                 grep -q "ln -sf /etc/nginx/sites-available/testclient.example.conf" "$FAKE/commands.log"
check "nginx reload logged"                    grep -q "systemctl reload nginx" "$FAKE/commands.log"
check "certbot logged"                         grep -q "certbot --nginx -d testclient.example" "$FAKE/commands.log"

echo "--- mock deploy re-run (idempotency)"
check "second run converges (exit 0)" "$SCRIPT_DIR/deploy_site.sh" --site "$TMP_SITE" \
  --domain testclient.example --email ops@example.com --mock "$FAKE"

echo "--- mock mailbox"
OUT="$("$SCRIPT_DIR/create_mailbox.sh" --domain testclient.example --user hello \
  --password 'S3cretTestPass' --mock "$FAKE")"
check "mailbox add logged"                     grep -q "setup email add hello@testclient.example" "$FAKE/commands.log"
check "password shown once on stdout"          grep -q "S3cretTestPass" <<<"$OUT"
check "password NOT in commands.log"           bash -c "! grep -q S3cretTestPass '$FAKE/commands.log'"

echo "--- dry-run leaves no trace"
snapshot() {
  python3 - "$FAKE" <<'PY'
import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1])
h = hashlib.sha256()
for path in sorted(root.rglob('*')):
    if path.is_file():
        h.update(str(path.relative_to(root)).encode())
        h.update(path.read_bytes())
print(h.hexdigest())
PY
}
SNAP_BEFORE="$(snapshot)"
"$SCRIPT_DIR/deploy_site.sh" --site "$TMP_SITE" --domain dryrun.example --dry-run > /dev/null
"$SCRIPT_DIR/create_mailbox.sh" --domain dryrun.example --dry-run > /dev/null
SNAP_AFTER="$(snapshot)"
check "dry-run changed nothing in fake vps"    test "$SNAP_BEFORE" = "$SNAP_AFTER"
check "dry-run created no dryrun.example conf" bash -c "! test -e '$FAKE/etc/nginx/sites-available/dryrun.example.conf'"

rm -rf "$TMP_SITE"
echo
echo "RESULT: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
