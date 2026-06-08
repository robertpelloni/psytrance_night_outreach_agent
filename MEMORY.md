# MEMORY

## Project Inception
- Initializing the repository for the `psytrance_night_outreach_agent`.
- Core goal: Automate venue scouting and outreach for psytrance events.

## Architecture Decisions
- SQLite for state management and data storage.
- Python for orchestrator/scraper due to rapid LLM integration and Playwright support.
- Flask for the HITL dashboard.

## Production Hardening (v1.1.46)
- **Scraper Resilience**: Implemented exponential backoff retry logic in `GoogleMapsPlaywrightScraper`.
- **Dynamic Proxy Rotation**: Implemented `ProxyRotator` with health tracking, success/failure reporting, and exponential backoff blacklisting (`fails^2 * 10s`).
- **Pipeline Isolation**: Added per-venue `try/except` blocks in `main.py` ensuring single-venue failures don't abort entire runs.
- **Bot Mitigation**: Integrated random rate limiting (2-5s) and user-agent rotation across all discovery loops.
- **CLI Intelligence**: Added `--dry-run` and `--city` flags to `main.py` for targeted and safe autonomous verification.
- **CI/CD Reliability**: Resolved blocking environment issues (empty `SMTP_PORT`) and module path resolution bugs in GitHub Actions.

## Detroit Refoundation (v1.1.44)
- Retargeted from 15 global cities to Detroit + Midwest circuit (Detroit, Hamtramck, Ferndale, Royal Oak, Ann Arbor, Grand Rapids, Chicago, Cleveland, Columbus, Toronto).
- Added artist identity system: `artist_name`, `collective_name`, `home_city` injected into all AI prompts.
- Vibe threshold lowered from 7 to 6 — Detroit psytrance is an untapped market, wider net needed.
- All AI prompts rewritten with Detroit scene context (techno birthplace, underground corridors, DIY culture).
- Added `detroit_relevance` trait to venue trait extraction.
- Neighborhood-aware search strategy: Corktown, Midtown, Southwest, Hamtramck, Ferndale each get dedicated queries.
- Multi-query search strategy: 9 Detroit-specific search phrases + neighborhood deep search + genre-specific queries per city.

## Key Codebase Traits
- Focus on underground electronic music subculture, especially psytrance/psychedelic trance.
- Dynamic genre adaptation for multi-niche outreach.
- High emphasis on "vibe" and professional outreach.
- Human-In-The-Loop as a critical safety feature.
- Modular scraper design (base class + specific implementations + AI-generated scrapers).
- Zero-dependency geospatial intelligence using AI for geocoding fallback.
- Proximity-based venue clustering for regional hotspot detection.
- Vision-enriched qualification using GPT-4o-vision for aesthetic vetting.
- Epsilon-greedy A/B pitch variant optimization (Professional/Underground/Technical).

## Known Gaps (as of v1.1.46)
- **No email inbox integration** — replies must be manually simulated (Phase 39).
- **No pipeline scheduling** or automated city cycle reset mechanism (Phase 40).
- **Settings UI incompleteness** — does not yet expose artist identity or Detroit-specific config (Phase 41).
- **Map Default** — defaults to world view instead of Detroit (42.3314, -83.0458).
- **Outreach Safety** — no daily throttle or OpenAI token budget tracking (Phase 42).
- **Data Model Gaps** — missing venue address, capacity, and neighborhood columns (Phase 43).
- **Pipeline Lifecycle** — no BOOKED or LOST statuses or automated negotiation machine (Phase 45).
- **Schema Migrations** — no system for safe database upgrades.
