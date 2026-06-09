# CHANGELOG

## [1.1.54] - 2026-06-09
### Added
- **Phase 45: Reply Automation & Negotiation Engine**: Implemented a negotiation state machine to track lead progress (INITIAL, REPLIED, NEGOTIATING, BOOKED, LOST).
- **OOO Auto-Response**: Integrated automated detection and re-queuing for "Out of Office" (OOO) replies, ensuring outreach isn't permanently stalled by temporary unavailability.
- **Negotiation Context**: Added `rate_card` and `availability_ranges` to the configuration, enabling the AI to draft context-aware responses to fee and scheduling inquiries.
- **Negotiation UI**: Overhauled the HITL Dashboard with "Mark as Booked/Lost" buttons, a dedicated Booked Tracker view, and visibility for the current negotiation status.

## [1.1.53] - 2026-06-09
### Added
- **Performance Documentation**: Created `PERFORMANCE.md` to establish the v1.1.46 technical performance baseline (100% stability).
- **Governance Updates**: Updated `MEMORY.md`, `TODO.md`, and `ROADMAP.md` to incorporate the stability report and schedule a dev-team review.

## [1.1.52] - 2026-06-09
### Added
- **Phase 43: Data Model & Persistence Improvements**: Expanded `venues` table with new columns: `address`, `phone`, `venue_type`, `capacity`, `neighborhood`, `source`, and `discovered_at`.
- **Automated Schema Migrations**: Implemented a migration utility in `DatabaseManager` to automatically update existing databases with new columns.
- **AI-Driven Data Enrichment**: Updated `AIEngine.extract_venue_traits` to automatically parse venue type, capacity, and neighborhood from venue descriptions.
- **Venue Detail UI Enhancement**: Updated the dashboard Venue Detail page to display the new extended metadata.
- **Source Tracking**: All primary scrapers (Google Maps, Resident Advisor) now tag the discovery source of each venue.

## [1.1.51] - 2026-06-08
### Fixed
- **Architectural Cleanup**: Removed `unittest.mock` usage from production dashboard code. Refactored `scheduled_pipeline` to use explicit argument passing for the `main()` orchestrator.
- **UI UX**: Updated default map view to center on Detroit (`42.3314, -83.0458`) for improved relevance to the current Midwest focus.

## [1.1.50] - 2026-06-08
### Added
- **Phase 40: Pipeline Scheduling & Cycle Management**: Integrated `APScheduler` into the dashboard to support automated weekly discovery and outreach runs.
- **Run History Tracking**: Added a `pipeline_runs` table and System Dashboard visualization to track start/end times, venue discovery counts, and lead generation metrics.
- **Operational Cycle Resets**: Implemented the ability to reset city-specific processing cycles via the dashboard or CLI (`--reset` flag).
- **Phase 42: Outreach Safety & Guardrails**: Implemented a daily outreach throttle (max 10 emails/day) and random delays between dispatches (5 minutes) to protect sender reputation.

### Fixed
- **System Stability**: Verified 100% pass rate on Master Integrity Suite in the production environment.
- **Dependency Management**: Updated `requirements.txt` with `APScheduler`.

## [1.1.49] - 2026-06-08
### Added
- **Phase 39: Email Inbox Integration**: Implemented automated IMAP-based reply fetching in `src/inbox_monitor.py` to monitor venue responses.
- **Intelligent Lead Matching**: Implemented a dual-strategy matching engine that links incoming emails to existing leads using either the sender's email address or a fallback venue name search within the email body.
- **Automated Reply Drafting**: Integrated `SentimentAnalyzer` to automatically classify incoming replies and generate AI-powered response drafts for "INTERESTED" or "INQUIRY" sentiments.
- **Dashboard UI Update**: Added a "Fetch New Replies" button to the HITL Dashboard, allowing manual triggers for inbox synchronization.
- **Pipeline Integration**: Wired the inbox polling cycle into the main `main.py` orchestrator, completing the autonomous feedback loop.

### Fixed
- **Test Suite Stability**: Resolved `sqlite3.OperationalError` in `tests/test_inbox_monitor.py` caused by passing `MagicMock` objects to database parameters.
- **Argparse Conflicts**: Fixed `SystemExit` errors in `tests/test_multi_genre_discovery.py` and `tests/test_autonomous_pipeline_e2e.py` by patching `sys.argv` during pipeline execution.

## [1.1.48] - 2026-06-08
### Added
- **Orchestration Optimization**: Refactored the discovery loop in `main.py` to distinguish between query-based and city-wide scrapers, ensuring efficient source traversal and reducing redundant requests.
- **Deep Proxy Feedback**: Integrated `ProxyRotator` feedback into the non-Playwright `ContactExtractor`, completing the health-tracking loop for all network requests.
- **Google Maps Enrichment**: Enhanced `GoogleMapsPlaywrightScraper` to extract website URLs directly from search results.
- **Enrichment-Only Separation**: Decoupled `InstagramScraper` from the discovery loop to focus on lead enrichment.

## [1.1.47] - 2026-06-08
### Added
- **Multi-Scraper Production Hardening**: Extended exponential backoff retry logic and standardized error isolation to Resident Advisor and Instagram scrapers.
- **Unified Proxy Reporting**: All scraper methods (search and enrichment) now report success/failure to `ProxyRotator` for intelligent pool management.

## [1.1.46] - 2026-06-07
### Added
- **Phase 38: Dynamic Proxy Rotation**: Further strengthen bot mitigation by tracking proxy health and rotating based on performance.
- **Proxy Health Tracking**: `ProxyRotator` now maintains success/failure counts for every proxy in the pool.
- **Intelligent Blacklisting**: Proxies that fail are temporarily blacklisted with an exponential backoff wait time (`fails^2 * 10s`).
- **Scraper Feedback Loop**: Integrated `report_success` and `report_failure` methods across all Playwright scrapers (Google Maps, RA, Instagram) to drive rotation logic.
- **Resilient Fallback**: If all proxies are blacklisted, the system automatically selects the one that will expire soonest.

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
