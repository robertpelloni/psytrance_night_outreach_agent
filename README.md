# Psytrance Night Outreach Agent

A Python application that automates venue scouting and booking outreach
for psytrance events, built for the Detroit scene: discover venues, enrich
and qualify them, generate personalized pitches with an LLM, send them
(with a human-in-the-loop review step, per its docs), monitor replies, and
handle follow-ups and negotiation.

## Pipeline

```
Hunt → Enrich → Qualify → Pitch → Review (HITL) → Dispatch → Follow Up → Negotiate
```

## Code

Substantial and real (~200 KB of Python across `main.py` and `src/`):

- `main.py` (~18 KB) — entry point; `start.sh`, `pilot_run.sh`,
  `deploy_staging.sh`, `deploy_production.sh`
- `src/scrapers/` + `src/scraper_generator.py` — venue discovery
  (Playwright/BeautifulSoup), including a Facebook Events discovery scraper
  (v1.2.1)
- `src/ai_engine.py` (~26 KB) — LLM pitch generation and reply handling
  (OpenAI API; keys via `.env.template`)
- `src/db_manager.py` (~33 KB), `database/` — venue/outreach state
- `src/outreach_engine.py`, `src/follow_up_engine.py`, `src/mailer.py`,
  `src/inbox_monitor.py` — sending, follow-ups, reply/bounce monitoring
- `src/negotiation/`, `src/sentiment_analyzer.py`,
  `src/outreach_predictor.py` — reply negotiation and scoring
- `src/analytics.py`, `src/tour_planner.py` (spherical K-Means tour
  clustering, v1.2.0), `src/dashboard/` — reporting, tour planning
  (see `generate_midwest_map.py`), dashboard
- `tests/` — pytest suite including E2E pipeline tests
  (`test_autonomous_pipeline_e2e.py`), with pytest-mock/pytest-cov

## On the claimed metrics

Earlier versions of this README advertised "100% pipeline stability", a
"100% pipeline success rate (Detroit Baseline)", and "88/88 tests PASSED".
Those numbers come from the project's own agent-written documents
(`PERFORMANCE.md`, `REVIEWS.md`) — there is no CI run or external record
in the repo to verify them against. Treat the metrics as self-reported.
The code volume and test files are real; whether the full pipeline has
ever run against live venues end-to-end is not established by anything
in this repo.

## Running

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.template .env   # add API keys / mail credentials
./start.sh
```

## Status

Active development through November 2026 (v1.2.1, last commit
2026-11-12). A serious prototype with real sending capability — which
is exactly why the HITL review step matters: run it in pilot mode
(`pilot_run.sh`) before letting it mail anyone.
