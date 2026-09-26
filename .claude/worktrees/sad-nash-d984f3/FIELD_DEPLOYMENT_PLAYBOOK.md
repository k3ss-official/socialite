# Field Deployment Playbook

Step-by-step from **lead name → live paid client**. Every command is copy-pasteable from
the repo root. Machine steps are automated; anything touching a real VPS, DNS, or money is
**manual and marked ⚠ MANUAL**. Companion docs: [FIRST_3_CLIENTS.md](FIRST_3_CLIENTS.md)
(who to sell to and how) and [SPRINT_48H.md](SPRINT_48H.md) (the schedule).

## The source-of-truth flow

```
"Business Name, Town, UK"
   │  ./run.sh  (= python -m socialite.cli run)
   ▼
FIND      data/leads/<id>/lead.json            score + no-website evidence   (free)
RESEARCH  data/leads/<id>/raw/                 pages, images, reviews        (free)
BIBLE     data/leads/<id>/bible/v<N>.json      claude -p, ~$0.90, cap $2     (LLM)
BUILD     data/leads/<id>/site/v<N>/           static bundle                 (free)
PITCH     data/leads/<id>/pitch/v<N>.html      gaps → ladder tiers           (free)
   │
   ▼ human sells (pitch sheet + demo)                       status: pitched
   ▼ dashboard /lead/<id> → Sign form → client + service ledger   status: signed
   ▼ ⚠ MANUAL: domain, DNS, provision/provision_client.sh, payment
   ▼ dashboard → advance status                              status: live
```

Statuses are forward-only for pipeline stages; the dashboard can move a lead anywhere.
Everything on disk under `data/leads/<id>/` is the source of truth; SQLite is only the
dashboard index; `data/events.jsonl` is the audit log.

## 0. One-time setup (before any client)

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
claude --version                      # bible stage shells out to claude CLI, must be logged in
bash provision/test_mock.sh           # must print: RESULT: 12 passed, 0 failed
```

⚠ MANUAL — VPS (once):
- Ubuntu-ish box with `nginx`, `certbot` (`python3-certbot-nginx`), `rsync`, and
  [docker-mailserver](https://github.com/docker-mailserver/docker-mailserver) running as
  container `mailserver`. SSH key auth for the deploy user (sudo for nginx/certbot or root).
- Demo wildcard DNS — **⚠ MANUAL, not yet created**. The exact record, once Tony confirms
  the VPS:

  ```
  Type A    Host *.demo    Domain k3ss.co.uk    Value <VPS-IP>
  ```

  i.e. `*.demo.k3ss.co.uk → <VPS-IP>`. This one record is what makes every
  `<lead-id>.demo.k3ss.co.uk` demo deploy get instant DNS + SSL with no per-client
  registrar work. Used by: the demo deploy commands below, SPRINT_48H.md hours 0–2 and
  5–7, and the FIRST_3_CLIENTS.md offer script.

Preflight (run from your Mac, replace `deploy@vps`):

```sh
ssh deploy@vps 'nginx -v && certbot --version && rsync --version | head -1 && docker ps --format "{{.Names}}" | grep mailserver'
dig +short anything.demo.k3ss.co.uk   # must return the VPS IP
```

## 1. Run the pipeline on a lead

```sh
./run.sh "The Woodsman, Chorley, UK"        # locale uk is default
```

Or sweep a whole town first (free, no LLM):

```sh
.venv/bin/python -m socialite.cli find-locale --locale uk --limit 25
.venv/bin/python -m socialite.cli status    # scores at a glance
```

**Acceptance checks before you leave the desk:**

```sh
.venv/bin/python dashboard/app.py           # → http://127.0.0.1:5057
```

- [ ] Lead score ≥ 80 and `website=none|dead|template` (never pitch a `real`-verdict lead).
- [ ] Open `bible/v<N>.json` in the dashboard — **read the `alerts` array**. Closures,
      phone/postcode conflicts, and prior-pitch (re-engagement) flags live there. An
      unresolved alert = do not pitch yet.
- [ ] Site preview looks right on mobile width; photos are actually the business's.
- [ ] Pitch sheet `pitch/v<N>.html` names real competitors and a recommended tier.
- [ ] Spend line shows under the $2 cap.

**Failure recovery:**

| Symptom | Fix |
|---|---|
| `claude CLI failed ... 401` | You're inside a Claude Code session leaking auth env — run from a plain terminal (llm.py scrubs known vars, but a clean shell is the sure path). Check `claude --version` logs in. |
| Overpass `406` on find-locale | Fixed (descriptive User-Agent in `socialite/web/overpass.py`); if it recurs the endpoint is rate-limiting — wait 60s and retry. |
| `cost cap` refusal | Real kill switch. Inspect spend in dashboard; if justified, raise `cost_cap_usd_per_lead` in `config/settings.yaml` deliberately. |
| Bible fails schema twice | Re-run `python -m socialite.cli bible <id> --force` (one repair pass is automatic; a fresh call usually lands). |
| Wrong/missing photos | Delete bad files from `data/leads/<id>/raw/images/`, then `bible --force` and `build`. |

Re-running anything is safe: hashes reuse cached work, statuses never regress.

## 2. Sell (see FIRST_3_CLIENTS.md for scripts)

Deploy the demo to your own wildcard subdomain so the prospect sees it live on their phone
— this touches only OUR infra, so it's routine:

```sh
provision/deploy_site.sh --site data/leads/<id>/site/v<N> \
  --domain <id>.demo.k3ss.co.uk --vps deploy@vps --email scousercheeky@gmail.com
curl -sI https://<id>.demo.k3ss.co.uk | head -1     # expect HTTP/2 200
```

Print the pitch sheet (`pitch/v<N>.html` → print to PDF). Pitch. When they say yes:

- Dashboard → lead → **Sign** form → tick rungs, enter agreed monthly £ → Sign.
- [ ] `/clients` now shows the client with MRR. This is the ledger of record.

## 3. Go live on the client's own domain — ⚠ MANUAL end to end

1. **Register the domain** (client pays or it's baked into Foundation). 
2. **DNS**: `A @ → <VPS-IP>`, `A www → <VPS-IP>`. For mail: `MX @ → mail host`, SPF TXT
   (`v=spf1 mx ~all`), DKIM per docker-mailserver docs. Wait until
   `dig +short clientdomain.co.uk` returns the VPS IP — **certbot fails before propagation**.
3. **Provision** (deploy + SSL + mailbox in one command):

```sh
provision/provision_client.sh --lead-id <id> \
  --domain clientdomain.co.uk --vps deploy@vps \
  --email scousercheeky@gmail.com --mail-user info
# see it first with --dry-run; both are idempotent and safe to re-run
```

4. **Record the mailbox password immediately** — printed once, never logged.

**Acceptance checks (the client is not live until all pass):**

```sh
curl -sI https://clientdomain.co.uk | head -1          # HTTP/2 200
curl -sI http://clientdomain.co.uk | grep -i location  # redirects to https
echo | openssl s_client -connect clientdomain.co.uk:443 2>/dev/null | openssl x509 -noout -dates
```

- [ ] Site renders on a real phone over mobile data (not your wifi).
- [ ] Send an email **to** info@clientdomain.co.uk from Gmail and **reply from** it
      (webmail/IMAP) — both directions land.
- [ ] Client has the mailbox credentials and confirmed login.
- [ ] Payment instruction is in place (see FIRST_3_CLIENTS.md).
- [ ] Dashboard → lead → advance status to **live**.

**Failure recovery:**

| Symptom | Fix |
|---|---|
| certbot fails | DNS not propagated or port 80 blocked. `dig +short domain`, retry provision (idempotent; skips cert if it later exists). |
| nginx -t fails | Bad vhost collision — `ssh deploy@vps 'ls /etc/nginx/sites-enabled'`, remove the stale conf, re-run. |
| Mail not arriving | Check MX/SPF records (`dig MX domain`), `docker logs mailserver`, and that port 25 isn't blocked by the VPS provider (common — request unblock). |
| Deployed wrong site version | `provision/deploy_site.sh --site data/leads/<id>/site/v<RIGHT>` — rsync `--delete` converges the docroot exactly. |
| Rollback | Redeploy the previous `site/v<N-1>` the same way. Nothing on the VPS is precious; artifacts on this machine are the truth. |

## 4. After go-live

- The service ledger (`/clients`) is the recurring-revenue truth: MRR per currency plus
  attrition projection. Attrition = set the service row's status in SQLite (Phase 2 will
  automate; for now it's one `UPDATE services SET status='cancelled'`).
- Monthly delivery obligations are whatever rungs were signed — the ladder
  (`config/ladder.yaml`) is the contract of what each rung includes.
