# GitHub Actions Setup

## Scheduled Workflows

Two workflows in `.github/workflows/`:
- `daily.yml` — runs `daily.py` at 9am UTC (3am Central)
- `weekly.yml` — runs `weekly.py` Fridays at 10am UTC (4am Central)

Both can also be triggered manually via the "Run workflow" button in GitHub.

## Required Secrets

In repo Settings → Secrets and variables → Actions:
- `GOOGLE_SERVICE_ACCOUNT_KEY` — full JSON contents of service account key file
- `ANTHROPIC_API_KEY` — API key for Claude

## Google Auth

Uses a service account with domain-wide delegation (configured in Google Workspace Admin Console) with scopes:
- `gmail.readonly`
- `documents`
- `spreadsheets`

The service account is: `docs-updater@qa-assistant-458920.iam.gserviceaccount.com`

## Local Development

When running locally (e.g., in solveit), auth falls back to OAuth pickle flow if `GOOGLE_SERVICE_ACCOUNT_KEY` env var is not set. See `google_auth.py`.
