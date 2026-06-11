# Provisioning

Idempotent deploy scripts. **These are written and mock-tested by the pipeline; a human
runs them against the real VPS.** Every script supports `--dry-run` (print, touch nothing)
and `--mock DIR` (simulate the VPS filesystem locally — how `test_mock.sh` proves them).

## Real-world usage

```sh
# everything for one client (latest built site version, deploy + mailbox):
provision/provision_client.sh --lead-id scran-away-chorley \
  --domain scranaway.co.uk --vps deploy@your-vps --email you@yourops.com

# see exactly what would happen first:
provision/provision_client.sh --lead-id scran-away-chorley --domain scranaway.co.uk --dry-run

# pieces individually:
provision/deploy_site.sh --site data/leads/<id>/site/v2 --domain example.co.uk --vps deploy@host
provision/create_mailbox.sh --domain example.co.uk --user info --vps deploy@host
```

## VPS prerequisites

- Ubuntu-ish with `nginx`, `certbot` (`python3-certbot-nginx`), `rsync`
- SSH key access for the deploy user; passwordless sudo for nginx/certbot or run as root
- [docker-mailserver](https://github.com/docker-mailserver/docker-mailserver) running as a
  container named `mailserver` (different stack? one comment block in `create_mailbox.sh`
  says what to swap)

## Hard requirements before running for real

- **DNS for the domain must already point at the VPS** — certbot will fail otherwise.
- Mailbox passwords are printed **once** to stdout and never logged. Record them immediately.

## Testing

```sh
provision/test_mock.sh   # full mock-mode proof, exits nonzero on failure
```
