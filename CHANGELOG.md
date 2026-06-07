# CHANGELOG

## [1.1.45] - 2026-06-07
### Added
- **Real-World Scraper Hardening**: Implemented exponential backoff retry logic in `GoogleMapsPlaywrightScraper` to handle transient network and selector errors.
- **Pipeline Resilience**: Added per-venue try/catch isolation in `main.py` to ensure a single failure does not abort the entire city run.
- **Rate Limiting**: Integrated random delays (2-5 seconds) between scraper calls to avoid IP bans.
- **Discovery Validation**: Added logic to reject venues with empty names or missing cities.
- **Pipeline Dry Run**: Added `--dry-run` flag to `main.py` for testing discovery and qualification logic without making AI calls or database writes.

### Fixed
- **E2E Test Regression**: Resolved `AssertionError` in `test_full_autonomous_cycle` by correctly ordering system logs for verification.
- **Multi-Genre Test Regression**: Updated `test_multi_genre_loop` to match the new Detroit-aware query generation logic.

## [1.1.44] - 2026-06-07
### Added
- **Detroit-Focus Refoundation**: Retargeted all cities from 15 global hubs to Detroit + Midwest circuit (Detroit, Hamtramck, Ferndale, Royal Oak, Ann Arbor, Grand Rapids, Chicago, Cleveland, Columbus, Toronto).
- **Artist Identity System**: New `artist_name`, `collective_name`, and `home_city` config fields. Identity is injected into all AI prompts (vibe check, pitch generation, follow-ups, reply drafts).
- **Detroit Neighborhood-Aware Search**: Pipeline now generates dedicated search queries for each Detroit neighborhood (Corktown, Midtown, Southwest, Eastside, New Center, Hamtramck, Ferndale) in addition to city-level queries.
- **Detroit-Specific Search Queries**: 9 custom Google Maps search phrases tuned for the Detroit underground scene (warehouse venue, DIY venue, afterhours, industrial venue, art space, etc.).
- **Detroit Scene Context in AI Prompts**: All AI prompts rewritten with knowledge of Detroit's techno heritage, underground corridors, DIY culture, and the psytrance gap in the market.
- **Detroit Trait Extraction**: Added `detroit_relevance` to venue trait extraction (detects "techno heritage", "Motor City", "underground" signals).
- **Multi-Query Search Strategy**: `main.py` now builds city-specific query lists via `build_search_queries()`. Detroit-area cities get neighborhood + scene queries; other cities get standard genre queries.
- **Intra-Run Venue Deduplication**: Pipeline deduplicates venues by (name, city) within a single run to prevent double-qualification from multiple search queries hitting the same venue.
- **Modular Pipeline Architecture**: Extracted `qualify_and_pitch()` function from `main.py` for cleaner separation of concerns.

### Changed
- **Vibe Threshold**: Lowered from 7 to 6 — Detroit psytrance is an untapped market requiring a wider net.
- **Pitch Variant Prompts**: All three variants (Professional, Underground, Technical) now include Detroit-specific guidance and scene-aware framing.
- **Pitch Generation Prompt**: Added key pitch elements: fill-the-gap positioning, low-risk first step suggestion, suburb/Detroit-specific acknowledgments.
- **Vibe Check Prompt**: Added Detroit scene context, expanded criteria (DIY spaces, proximity to underground corridors), and explicit low-score criteria (sports bars, bottle-service clubs, live-band-only venues).
- **Vision Analysis Prompt**: Added Detroit-specific aesthetic signals (exposed brick, industrial aesthetic, raw/unfinished vibe).
- **ConfigManager Defaults**: Fully rewritten with Detroit-focused defaults, artist identity fields, and Detroit-specific configuration.
- **AIEngine Type Safety**: Fixed all `str | None` type issues with OpenAI response handling (no more calling `.strip()` or `json.loads()` on potentially-None values).

### Removed
- **Global City List**: Removed Goa, Melbourne, Zurich, Sao Paulo, Tel Aviv, Amsterdam, Cape Town, Koh Phangan, San Francisco, Berlin, London, Tokyo, Lisbon from default config. These can be re-added by the user.

## [1.1.43] - 2024-06-02
### Verified
- **Sync Integrity**: Successfully executed the Repository Synchronization Protocol, confirming dual-direction merge logic and Master Integrity Suite compliance.
- **E2E Stability**: Fixed a critical regression in the autonomous pipeline E2E test by ensuring proper database isolation and mocking for `AnalyticsEngine`.

### Added
- **Sentiment-Driven Variant Optimization**: Implemented an epsilon-greedy algorithm in the main pipeline to automatically select high-converting pitch variants based on historical interested replies.
- **A/B Performance Analytics**: Added a new performance table to the Analytics Dashboard, visualizing conversion rates (Interested / Sent) per variant with real-time progress bars.
- **Conversion-Aware Discovery**: Refactored `AnalyticsEngine` to support aggregated metric retrieval for data-driven qualification.

### Changed
- **Pipeline Intelligence**: The orchestrator now balances 20% exploration (random variants) with 80% exploitation of the current winning strategy.

## [1.1.40] - 2024-06-01
### Added
- **Vision-Enriched Venue Qualification**: Integrated GPT-4o-vision into the qualification pipeline for aesthetic vetting.
- **Visual Metadata Extraction**: Updated Google Maps and Resident Advisor scrapers to capture venue images.
- **Aesthetic Vibe Scoring**: Implemented `analyze_visual_vibe` in AIEngine.
- **Vision Dashboard Integration**: Enhanced HITL Dashboard with venue images and visual analysis.
- **Schema Expansion**: Added `image_url` and `visual_description` to venues table.

## [1.1.35] - 2024-05-31
### Added
- **Master Genre Dynamic Adaptation**: Refactored the entire AI and scouting pipeline to support any electronic music genre.
- **Configurable Active Genre**: Pipeline uses the first genre in `target_genres` as the active genre.
- **Lead Genre Tracking**: Added `qualified_genre` to leads schema.

## [1.1.28] - 2024-05-30
### Added
- **Outreach Predictor**: Success probability based on vibe score, city history, and AI trait alignment.
- **Success Probability Visualization**: Integrated into HITL dashboard.

## [1.1.22] - 2024-05-27
### Added
- **Geographic Intelligence**: Nominatim + AI-fallback geocoding.
- **Interactive Lead Mapping**: Leaflet.js map with vibe-score visualization.

## [1.1.12] - 2024-05-26
### Added
- **AI-Driven Trait Extraction**: Sound system, lighting, atmosphere traits from venue descriptions.
- **Hyper-Personalized Pitching**: Traits integrated into AI pitch generation.

## [1.0.0] - 2024-05-24
### Added
- **Production Milestone**: Full integration of all pipeline stages.
- **HITL Dashboard**: Review, approve, reject, regenerate pitches.
- **SMTP Dispatch**: Automated email sending.
- **Sentiment Analysis**: Reply classification and draft orchestration.
- **Follow-up Engine**: Automated nudge cycle.
- **Proxy/UA Rotation**: Anti-bot bypass.
