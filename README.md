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

Substantial and real (~150 KB of Python):

- `main.py` (~18 KB) — entry point; `start.sh`, `pilot_run.sh`,
  `deploy_staging.sh`, `deploy_production.sh`
- `src/scrapers/` + `src/scraper_generator.py` — venue discovery
  (Playwright/BeautifulSoup)
- `src/ai_engine.py` (~25 KB) — LLM pitch generation and reply handling
  (OpenAI API; keys via `.env.template`)
- `src/db_manager.py` (~25 KB), `database/` — venue/outreach state
- `src/outreach_engine.py`, `src/follow_up_engine.py`, `src/mailer.py`,
  `src/inbox_monitor.py` — sending, follow-ups, reply/bounce monitoring
- `src/negotiation/`, `src/sentiment_analyzer.py`,
  `src/outreach_predictor.py` — reply negotiation and scoring
- `src/analytics.py`, `src/tour_planner.py`, `src/dashboard/` — reporting,
  tour planning (see `generate_midwest_map.py`), dashboard
- `tests/` — pytest suite including E2E pipeline tests
  (`test_autonomous_pipeline_e2e.py`), with pytest-mock/pytest-cov

## On the claimed metrics

The README this replaces advertised "100% pipeline stability", a "100%
pipeline success rate (Detroit Baseline)", and "88/88 tests PASSED
(v1.1.63)". Those numbers come from the project's own agent-written
documents (`PERFORMANCE.md`, `REVIEWS.md`) — there is no CI run or external
record in the repo to verify them against, and `VERSION.md` (1.1.77)
doesn't even match the version the claims cite (v1.1.63). Treat the
metrics as self-reported. The code volume and test files are real; whether
the full pipeline has ever run against live venues end-to-end is not
established by anything in this repo.

## Running

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.template .env   # add API keys / mail credentials
./start.sh
```

## Status

Built May–July 2026 in agent sessions; latest commits are July 2026
feature merges. A serious prototype with real sending capability — which
is exactly why the HITL review step matters: run it in pilot mode
(`pilot_run.sh`) before letting it mail anyone.
