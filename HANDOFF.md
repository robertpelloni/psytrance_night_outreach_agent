# SESSION HANDOFF - v1.1.44

## OVERVIEW
This session focused on **Detroit-Focus Refoundation**: retargeting the entire agent from a global 15-city system to a Detroit-psytrance-specific tool with artist identity, neighborhood-aware search, and scene-contextualized AI prompts. Additionally, a comprehensive gap analysis was performed and all project documentation was rewritten.

## STRUCTURAL SHIFTS & ARCHITECTURE
- **City List Replaced**: 15 global hubs → Detroit + Midwest circuit (10 cities)
- **Artist Identity Layer**: `artist_name`, `collective_name`, `home_city` now injected into all AI prompts via `_get_identity_context()`
- **Neighborhood Search Strategy**: `build_search_queries()` generates Detroit-specific queries per neighborhood + scene-specific phrases + genre queries
- **Detroit Scene Context**: All AI prompts (vibe check, pitch, follow-up, vision, reply draft) rewritten with Detroit underground knowledge
- **Vibe Threshold**: Lowered from 7 → 6 to cast wider net in untapped market
- **Pipeline Modularization**: `qualify_and_pitch()` extracted from `main.py`
- **Intra-Run Deduplication**: Venues deduplicated by (name, city) within a single pipeline run

## KEY ACHIEVEMENTS (v1.1.44)
1. **Detroit-First Pipeline**: Every search query, AI prompt, and config default is now shaped for the Detroit psytrance scene
2. **Artist Identity**: Pitches now reference the actual artist/collective, not generic text
3. **Neighborhood Coverage**: 8 Detroit neighborhoods get dedicated search queries
4. **Comprehensive Gap Analysis**: Identified 15+ critical missing features across 8 categories
5. **Documentation Overhaul**: Rewrote README, VISION, ROADMAP, TODO, IDEAS, MANUAL, DEPLOY, CHANGELOG, MEMORY, VERSION
6. **New .env.template**: Created for onboarding
7. **AIEngine Type Safety**: Fixed all `str | None` issues with OpenAI response handling

## DISCOVERIES & LEARNED PATTERNS
- **Config Schema Mismatch**: Settings UI saves only 5 fields but config.json has 15+ fields. The POST handler in `app.py` will silently drop fields it doesn't know about.
- **CSS Selector Fragility**: Google Maps selectors (`.m677R`, `.hfpxzc`) are known to change frequently. The scraper needs a fallback API strategy.
- **No Per-Venue Error Isolation**: A single bad venue object can crash the entire city processing loop. Each venue should be processed in its own try/catch.
- **City Processing Log is a Dead End**: Once a city is marked COMPLETED, there's no UI or CLI way to reset it. Users must manually edit the database.
- **Pitch Subject Hardcoding**: Subject lines like "Proposal for Psytrance Night Residency" are hardcoded in `outreach_engine.py` and `app.py`, ignoring the genre configuration.

## UPCOMING MILESTONES (Phases 37–46)
- **Phase 37**: Scraper hardening (retry logic, error isolation, rate limiting, validation)
- **Phase 38**: IMAP inbox integration (auto-ingest venue replies)
- **Phase 39**: Pipeline scheduling + cycle reset (APScheduler, run history)
- **Phase 40**: Settings UI completeness (artist identity, media library, Detroit fields)
- **Phase 41**: Outreach safety (throttle, token budget, DNC list, AI subject lines)
- **Phase 42**: Data model improvements (address, capacity, venue_type, neighborhood, source, indexes, migrations)
- **Phase 43**: Detroit venue seed + manual venue entry + additional scrapers
- **Phase 44**: Negotiation engine (state machine, BOOKED/LOST statuses, booking tracker)
- **Phase 45**: Reporting & scene analytics (funnel, warmth scores, CSV export)
- **Phase 46**: Multi-artist & collaboration support

## SYSTEM STATE
- **Version**: 1.1.44
- **Database**: `database/outreach.db` (Schema v1.1.40 — unchanged)
- **Primary Branch**: `main`
- **Integrity**: Test suite has pytest dependency issue on Python 3.14 (chromadb/pydantic conflict) — needs pinned requirements
