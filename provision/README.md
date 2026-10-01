# Deployment and mail

These scripts deploy an existing static bundle to an explicitly selected VPS and can
create a mailbox. They are separate from research and preview. Mock/dry-run tests are
not evidence that a real host, DNS, SSL or mail delivery has been verified.

## Prerequisites

Run from the local repository with the socialite Conda environment active; Python 3.12
renders the fixed nginx template. No envsubst installation is required. Real deployment
also needs SSH/rsync, an Ubuntu-style host with nginx and certbot, and DNS pointing to
that host. Mailbox creation assumes docker-mailserver in a container named mailserver.
Review or adapt that assumption before using a different mail stack.

## Inspect and test

```sh
bash provision/test_mock.sh
bash provision/deploy_site.sh --site data/leads/LEAD/site/v1 --domain example.co.uk --dry-run
bash provision/create_mailbox.sh --domain example.co.uk --dry-run
```

The mock harness uses temporary folders outside the repository, checks repeated
deployment and compares file names/content to prove dry-run leaves them unchanged.

## Explicit real deployment

Only use an approved client/domain/host and an already reviewed built bundle:

```sh
bash provision/provision_client.sh --lead-id LEAD --domain client.example \
  --vps deploy@your-host --email ops@your-domain.example --dry-run
```

Inspect the dry-run, then invoke the same command without that flag when publication
is authorised. Or use deploy_site.sh and create_mailbox.sh separately. Mailbox passwords
are emitted once and must be recorded privately; never put them in Git or client reports.

Verify rendered content on mobile, HTTP-to-HTTPS redirect, certificate/domain and both
directions of mail before marking a client live. Configure appropriate MX/SPF/DKIM
for the actual provider. Payment arrangements and recurring delivery must be agreed;
a proposed ladder is not proof of an executed service.

The local client/service/job ledger is durable SQLite storage. Back it up alongside the
artifact tree. Restore a previous built site version for a site rollback rather than
assuming the VPS contains the only copy. No deployment is performed by starting a
research or preview job.
