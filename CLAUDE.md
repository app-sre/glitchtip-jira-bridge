# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Red Hat AppSRE service that receives GlitchTip alert webhooks and turns them into Jira tickets, deduplicating via a DynamoDB-backed cache and rate-limiting ticket creation per Jira project.

## Commands

```bash
make format   # ruff check (autofix) + ruff format
make test     # ruff check --no-fix, ruff format --check, mypy, pytest (with coverage)
```

Run a single test: `uv run pytest tests/backends/test_jira.py::test_name -vv`

Local stack (SQS + DynamoDB via localstack, web app, celery worker):

```bash
docker compose up localstack   # start localstack first
GJB_START_MODE=web ./app.sh    # in one terminal
GJB_START_MODE=worker ./app.sh # in another
```

`app.sh` sources `settings.conf` (gitignored, not present by default) for local secrets, e.g. `GJB_JIRA_API_KEY` from staging Jira.

## Architecture

Request flow: **FastAPI (`api/v1/alert.py`) → Celery task (`tasks.py`) → Jira backend (`backends/jira.py`)**, with DynamoDB-backed cache/rate-limiting (`backends/db.py`) in between.

- `POST /api/v1/alert/{jira_project_key}` accepts a `GlitchtipAlert` (Slack-style webhook payload with `attachments`, defined in `models.py`) and, for each attachment, enqueues a `create_jira_ticket` Celery task — request handling never talks to Jira or DynamoDB directly.
- `tasks.py` builds fresh `boto3` DynamoDB and `JIRA` clients per task invocation and calls `backends.jira.create_issue`. On any exception it retries via Celery (`settings.retries` / `settings.retry_delay`).
- `backends/jira.py::create_issue` is the core dedup/create/reopen state machine:
  1. Check `IssueCache` (DynamoDB, TTL'd) for the GlitchTip issue URL — if cached, skip entirely.
  2. Otherwise search Jira by JQL (`labels = '<url>'` scoped to the project) since the cache can be cold/expired while the ticket still exists.
  3. If no Jira issue exists, check `Limits` (DynamoDB, per-project sliding window) before creating a new one.
  4. If a Jira issue exists and its resolution isn't "Won't Do", reopen it via the first available transition.
  5. Always (re-)write the cache entry at the end.
  6. JQL string literals are escaped via `_escape_jql_string` — never interpolate raw user/alert input into JQL without it.
- The web process (`main.py`) and worker process (`worker.py`) are the same codebase started in different modes (`GJB_START_MODE=web|worker` in `app.sh`), sharing `config.py` settings and the Celery app defined in `tasks.py`.
- Auth: API key passed as `Authorization: Bearer <key>` header or `?token=` query param (GlitchTip cannot send custom headers) — see `dependencies.py::api_key_auth`. Because the token can leak into the query string, `logging_utils.py::RedactTokenQueryParamFilter` is attached to `uvicorn.access` to scrub it from logs; keep that filter in place if touching logging setup. Auth is skipped entirely when `GJB_DEBUG=1`.
- `config.py::Settings` reads from env vars (`GJB_` prefix) by default, but in-cluster it reads secrets from files mounted at `/var/run/secrets/glitchtip-jira-bridge` (see `resolve_secrets_dir`) — local/dev and docker-compose keep using env vars/`settings.conf`.
- Metrics (`metrics.py`, Prometheus) are incremented at each state transition in `create_issue`/`tasks.py` (`received_alerts`, `tickets_created`, `tickets_reopened`, `limit_reached`) and exposed via `prometheus-fastapi-instrumentator` (web) or `prometheus_client.start_http_server` (worker, port `GJB_WORKER_METRICS_PORT`).

## Conventions

- Python 3.14, managed with `uv` (not poetry, despite the README).
- `ruff` runs with `select = ["ALL"]`; see `pyproject.toml` for the ignore list before assuming a rule applies.
- mypy strict-ish config: `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`, `warn_unused_ignores` all on — type everything.
- Never suppress a ruff/mypy finding with an ignore comment without checking `pyproject.toml`'s existing ignore list first — many stylistic rules are already disabled there.
