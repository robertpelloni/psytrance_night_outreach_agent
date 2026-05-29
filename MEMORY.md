# MEMORY

## Project Inception
- Initializing the repository for the `psytrance_night_outreach_agent`.
- Core goal: Automate venue scouting and outreach for psytrance events.

## Architecture Decisions
- SQLite for state management and data storage.
- Python for orchestrator/scraper due to rapid LLM integration and Playwright support.
- Flask for the HITL dashboard.

## Codebase Traits
- Focus on underground subculture (psytrance).
- High emphasis on "vibe" and professional outreach.
- Human-In-The-Loop as a critical safety feature.
- Modular scraper design (base class + specific implementations).
