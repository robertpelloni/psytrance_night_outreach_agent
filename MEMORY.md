# MEMORY

## Project Inception
- Initializing the repository for the `psytrance_night_outreach_agent`.
- Core goal: Automate venue scouting and outreach for psytrance events.

## Architecture Decisions
- SQLite for state management and data storage.
- Python for orchestrator/scraper due to rapid LLM integration and Playwright support.
- Flask for the HITL dashboard.

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

## Known Gaps (as of v1.1.44)
- No email inbox integration — replies must be manually simulated.
- Scrapers use brittle CSS selectors with no retry logic or per-venue error isolation.
- No pipeline scheduling or city cycle reset mechanism.
- Settings UI doesn't expose artist_name, collective_name, media_library, or Detroit-specific fields.
- Map defaults to world view instead of Detroit.
- No outreach throttle or token budget tracking.
- No venue address, capacity, venue_type, neighborhood, or source columns in database.
- No BOOKED or LOST pipeline statuses for tracking the full lifecycle.
- No schema migration system for safe upgrades.
- Pitch subject lines are hardcoded, not AI-generated.
