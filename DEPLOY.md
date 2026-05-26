# DEPLOY

## Prerequisites
- Python 3.9+
- Playwright (`playwright install chromium`)
- OpenAI API Key (set in `.env`)

## Local Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install Playwright browsers: `playwright install chromium`
6. Create a `.env` file based on `MANUAL.md` (OpenAI, SMTP, Proxy settings).
7. Initialize the database: (Automatically handled by `DatabaseManager`)

## Running the Pipeline
`python main.py`

## Running the Dashboard
`python src/dashboard/app.py`

## Repository Synchronization
The repository includes an automated synchronization protocol that runs daily via GitHub Actions (`.github/workflows/sync.yml`). This ensures that feature branches are merged into `main` if they contain unique progress, and `main` is synced back into active feature branches.

To run the sync manually:
`python scripts/sync_repo.py`

## CI/CD Pipeline (GitHub Actions)
The synchronization protocol is fully integrated into GitHub Actions. For the pipeline to function correctly, the following **GitHub Secrets** must be configured in the repository settings:

- `OPENAI_API_KEY`: Required for vibe-checking, pitch generation, and AI conflict resolution.
- `PROXY_LIST`: Comma-separated list of proxies (e.g., `http://user:pass@host:port`).
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Credentials for the booking email.
- `SENDER_EMAIL`: The outbound email address (e.g., `booking@yourdomain.com`).

The pipeline triggers on every push to **any** branch (`**`), ensuring continuous synchronization across the entire repository. Note that the full outreach pipeline (`main.py`) only executes on the `main` branch or scheduled runs to optimize API usage.

## Tiered Deployment Architecture

### 1. Feature Environment (Local / CI Sync)
- **Trigger**: Every push to any branch.
- **Actions**: Continuous repository synchronization and unit testing via `.github/workflows/sync.yml`.
- **Purpose**: To keep all branches up-to-date and ensure local development doesn't drift.

### 2. Staging Environment (Release Candidate)
A dedicated staging workflow is configured in `.github/workflows/staging.yml`.
- **Trigger**: Push to the `staging` branch.
- **Actions**: Sets up a clean environment, initializes `database/staging_outreach.db`, and executes the full end-to-end integration suite (`tests/test_smoke.py` and `tests/test_protocol_e2e.py`).
- **Purpose**: To verify that upcoming releases are functionally sound before merging into `main`.
- **Manual Command**: `./deploy_staging.sh`

### 3. Production Environment (Live Deployment)
- **Trigger**: Push to the `main` branch.
- **Workflow**: `.github/workflows/production.yml`.
- **Actions**: Refreshes production environment, executes the **Master Integrity Suite** (all 20+ tests), and logs the deployment event to the dashboard.
- **Manual Command**: `./deploy_production.sh`

## Live Pilot Validation
Before moving to full 24/7 autonomous operation, execute a live pilot run to verify connectivity and external service limits:
`./pilot_run.sh`
This script runs connectivity diagnostics, performs a single-city discovery cycle, and synchronizes the results.
