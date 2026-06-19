# MEMORY

## Project Inception
- Initializing the repository for the `psytrance_night_outreach_agent`.
- Core goal: Automate venue scouting and outreach for psytrance events.

## Architecture Decisions
- SQLite for state management and data storage.
- Python for orchestrator/scraper due to rapid LLM integration and Playwright support.
- Flask for the HITL dashboard.

## Production Hardening (v1.1.63)
- **Stability Baseline**: Maintained 100% pipeline stability across 88 tests in the Master Integrity Suite; documented in `PERFORMANCE.md`. This baseline confirms the system's readiness for multi-artist production operations.
- **CI/CD Quality Gate**: Deployment pipeline (v1.1.55) mandates stability verification (PERFORMANCE.md) and final QA sign-off for both staging and production environments. Verified for staging v1.1.63.
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

## Autonomous Feedback Loop (v1.1.58)
- **Email Inbox Integration**: Implemented IMAP-based reply fetching in `src/inbox_monitor.py` (Phase 39).
- **Automated Negotiation**: Implemented a state machine (INITIAL -> REPLIED -> NEGOTIATING -> BOOKED/LOST) with OOO detection and auto-requeue (Phase 45).
- **Pipeline Scheduling**: Integrated `APScheduler` for weekly discovery and outreach cycles with run history tracking (Phase 40).
- **Outreach Safety**: Implemented daily dispatch throttles (10/day) and random jitter (5m) to protect sender reputation (Phase 42).
- **Advanced Analytics**: Implemented conversion funnels (Discovered -> Qualified -> Pitched -> Replied -> Booked) and "Venue Warmth" scoring (Phase 46).
- **Data Persistence**: Expanded `venues` table with technical metadata (capacity, type, neighborhood) and implemented auto-migrations in `DatabaseManager` (Phase 43).
- **UX Optimization**: Centered dashboard map on Detroit (v1.1.51) and overhauled Settings UI for Detroit-specific search phrases and artist identity.

## Known Gaps (as of v1.1.64)
- **OpenAI Token Budgeting**: No automated cost estimation or alerting per pipeline run (Phase 42).
- **Visual Analytics**: Missing outreach timeline visualization and side-by-side venue comparison (Phase 46).
- **Multi-Artist Support**: Collective-level artist profiles and shared dashboard access pending (Phase 47).
