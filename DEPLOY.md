# DEPLOY

## Prerequisites
- Python 3.9+ (3.11+ recommended)
- Playwright (`playwright install chromium`)
- OpenAI API Key (set in `.env`)

## Local Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Install Playwright browsers: `playwright install chromium`
6. Create a `.env` file (see MANUAL.md for all variables).
7. Edit `database/config.json` with your artist name, EPK link, and target cities.
8. Database initializes automatically on first run.

## Running the Pipeline
```bash
python main.py
```

## Running the Dashboard
```bash
python src/dashboard/app.py
# Access at http://localhost:5000
```

## Resetting a City Cycle
Once a city is processed, it's skipped on subsequent runs. To re-run discovery for a city:
- Use the Dashboard System tab → "Reset All Cycles" (Phase 40)
- Or programmatically: `db.mark_city_processed("Detroit", status="PENDING")`

## Repository Synchronization

The repository includes an automated synchronization protocol that runs daily via GitHub Actions (`.github/workflows/sync.yml`). This ensures that feature branches are merged into `main` if they contain unique progress, and `main` is synced back into active feature branches.

To run the sync manually: `python sync_repo.py`

### Automated Local Sync (Git Hook)
Install a `post-commit` hook that triggers `sync_repo.py` after every local commit:
```bash
./install_hooks.sh
```

## CI/CD Pipeline (GitHub Actions)

The following **GitHub Secrets** must be configured:

| Secret | Purpose |
|--------|---------|
| `OPENAI_API_KEY` | Vibe-checking, pitch generation, AI conflict resolution |
| `PROXY_LIST` | Comma-separated proxy URLs |
| `SMTP_SERVER` | SMTP host for booking emails |
| `SMTP_PORT` | SMTP port |
| `SMTP_USER` | SMTP username |
| `SMTP_PASSWORD` | SMTP password |
| `SENDER_EMAIL` | Outbound booking email address |
| `IMAP_SERVER` | IMAP host for fetching replies |
| `IMAP_USER` | IMAP username |
| `IMAP_PASSWORD` | IMAP password |

The pipeline triggers on every push to **any** branch. The full outreach pipeline (`main.py`) only executes on `main` or scheduled runs to optimize API usage.

## Tiered Deployment Architecture

### 1. Feature Environment (Local / CI Sync)
- **Trigger**: Every push to any branch.
- **Actions**: Repository synchronization and unit testing via `.github/workflows/sync.yml`.
- **Purpose**: Keep all branches up-to-date and ensure local development doesn't drift.

### 2. Staging Environment (Release Candidate)
- **Trigger**: Push to the `staging` branch.
- **Workflow**: `.github/workflows/staging.yml`
- **Actions**: Clean environment, `database/staging_outreach.db`, full E2E suite.
- **Manual Command**: `./deploy_staging.sh`

### 3. Production Environment (Live Deployment)
- **Trigger**: Push to the `main` branch.
- **Workflow**: `.github/workflows/production.yml`
- **Actions**: Master Integrity Suite (all tests), **PERFORMANCE.md verification**, deployment event logging.
- **Manual Command**: `./deploy_production.sh`

> **Note on Performance Verification:** Every production deployment automatically verifies that `PERFORMANCE.md` confirms 100% pipeline stability before proceeding.

## Live Pilot Validation

Before full autonomous operation, execute a pilot run:
```bash
./pilot_run.sh
```
This runs connectivity diagnostics, a single-city discovery cycle, and synchronizes results.

## Token Cost Awareness

Each full pipeline run makes multiple GPT-4o calls per venue:
- 1 × vibe check (~500 tokens)
- 1 × trait extraction (~400 tokens)
- 1 × pitch generation (~800 tokens)
- Optional: 1 × vision analysis (~300 tokens)
- Optional: 1 × media selection (~200 tokens)

**Rough cost**: ~$0.05–0.10 per qualified venue at GPT-4o pricing. A 50-venue run ≈ $2.50–5.00.

A token budget tracker and dry-run mode are planned (Phase 41).
