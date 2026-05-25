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
6. Create a `.env` file with `OPENAI_API_KEY=your_key_here`.
7. Initialize the database: (Automatically handled by `DatabaseManager`)

## Running the Pipeline
`python main.py`

## Running the Dashboard
`python src/dashboard/app.py`

## Repository Synchronization
The repository includes an automated synchronization protocol that runs daily via GitHub Actions (`.github/workflows/sync.yml`). This ensures that feature branches are merged into `main` if they contain unique progress, and `main` is synced back into active feature branches.

To run the sync manually:
`python scripts/sync_repo.py`
