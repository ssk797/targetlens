# Security Policy

## Public and private data boundary

This repository contains application source code and curated public target-research examples only. It must not contain real API keys, production credentials, user questions, private research sessions, source snapshots, or internal knowledge-graph records.

The public library endpoints are intentionally read-only. Workspace session and evidence endpoints require an authenticated account and are filtered to the current account (plus explicitly marked demo records).

## Local development

- Keep provider keys in `apps/api/.env`; `.env` files are ignored by Git.
- Docker Compose ports are bound to `127.0.0.1` for local development.
- Replace every local example credential through deployment environment variables or a managed secret store.
- Do not deploy the development Compose configuration directly to a public host.

## Reporting a vulnerability

Do not include credentials, personal data, unpublished research, or exploitable details in a public Issue. Contact the repository owner privately or use GitHub's private vulnerability reporting when enabled.

## Supported version

Security fixes target the current `main` branch.
