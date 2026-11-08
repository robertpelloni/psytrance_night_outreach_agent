# CHANGELOG

## [1.1.88] - 2026-11-05

### Added
- **Email Engagement & Pixel Tracking Infrastructure (`database/schema.sql`, `src/db_manager.py`)**: Added `email_tracking_events` table and data manager methods for recording and summarizing opens and link clicks with IP addresses and user agents.
- **Multipart Tracked Email & Link Wrapping (`src/mailer.py`)**: Enhanced `Mailer.send_email()` to generate multipart HTML emails embedding 1x1 transparent GIFs (`/track/open/<lead_id>.gif`) and auto-wrapping audio/EPK hyperlinks (`/track/click/<lead_id>?url=...`).
- **Tracking Endpoints (`src/dashboard/app.py`)**: Added `/track/open/<lead_id>.gif` (serving un-cached transparent GIF) and `/track/click/<lead_id>` (recording interaction and redirecting safely).
- **Engagement Metrics UI (`src/dashboard/templates/index.html`, `venue_detail.html`)**: Surfaced open/click badges on queue cards, an Email Engagement KPI strip on the Analytics tab (Open Rate, CTR, gross opens, gross clicks), and an engagement activity timeline on venue dossier pages.
- **Email Tracking Test Suite (`tests/test_email_tracking.py`)**: Added unit and integration tests covering database logging, HTML link wrapping, GIF endpoint serving, and click redirections.

## [1.1.87] - 2026-11-05

### Added
- **Eventbrite Nightlife Discovery Scraper (`src/scrapers/eventbrite.py`)**: Implemented `EventbriteWebScraper` for automated discovery of nightlife, warehouse, and electronic music venues via Eventbrite event listings using schema.org JSON-LD and HTML card fallbacks.
- **Dynamic Scraper Discovery Integration**: Automatically registered `EventbriteWebScraper` into `main.py` query scrapers and displayed `eventbrite.py` as an operational module in the Scraper Sources tab of the Unified Command Center.
- **Eventbrite Scraper Test Suite (`tests/test_eventbrite_scraper.py`)**: Added unit and integration tests verifying JSON-LD parsing, card fallbacks, rate limit backoff resilience, and query execution.

## [1.1.86] - 2026-11-05

### Added
- **Collaborative Filtering & Alternate Venue Recommendation Engine (`src/recommendation_engine.py`)**: Implemented `RecommendationEngine` to compute multi-factor affinity scoring across acoustic profiles (Funktion-One, Void, Danley), venue capacities, spatial proximity via Haversine distance decay, and historical booking outcomes.
- **Recommendations API (`src/dashboard/app.py`)**: Added `/recommend_venues/<venue_id>` endpoint supporting customizable result limits, minimum similarity score filters, and automatic exclusion of previously rejected venues.
- **Interactive Sibling Recommendations UI (`src/dashboard/templates/index.html` & `venue_detail.html`)**: Added "Alternate Venues" quick-action buttons on lead cards and venue dossier pages, launching an interactive recommendations modal with composite affinity badges, shared trait tags, transit distance badges, and direct links to venue dossiers.
- **Collaborative Filtering Test Suite (`tests/test_recommendation_engine.py`)**: Added unit and integration tests covering trait set extraction, distance decay weighting, exclusion of rejected targets, and REST API responses.

## [1.1.85] - 2026-11-05

### Added
- **DBSCAN Dynamic Density & Transit Clustering Metrics (`src/analytics.py`)**: Enhanced `AnalyticsEngine.get_venue_clusters()` to calculate geographic bounding-box radius (`cluster_radius_km`) and inter-city transit drive times (`est_intercity_drive_hrs`) at nominal transit speed (80 km/h) for venue clusters.
- **Active Touring Clusters & Transit Densities UI (`src/dashboard/templates/index.html`)**: Integrated corridor density metrics, cluster span radius badges, and drive-time calculations into the Geographic Map & Circuit Optimizer tab with quick-filter links.
- **Advanced Dynamic Clustering Test Suite (`tests/test_advanced_clustering.py`)**: Added comprehensive tests verifying cluster radius calculation, inter-city driving time estimation, and bounding-box perimeter analysis for DBSCAN geographic groupings.

## [1.1.84] - 2026-11-05

### Added
- **Curator Intelligence in AI Engine (`src/ai_engine.py`)**: Enhanced `AIEngine.generate_pitch()` and `AIEngine.vibe_check()` to ingest confidential curator notes and field annotations, dynamically incorporating sound engineer preferences, sound specs, and door policies into AI-generated pitches and re-evaluations.
- **Pipeline & Dashboard Call-Site Propagation**: Wired `db.get_venue_notes()` into `main.py` (`qualify_and_pitch`) and `src/dashboard/app.py` (`/bulk_action`, `/requalify`, `/regenerate`).
- **Venue Notes AI Injection Test Suite (`tests/test_notes_in_pitch.py`)**: Added unit tests verifying prompt formatting and context propagation for curator notes in pitch generation and vibe scoring.

## [1.1.83] - 2026-11-05

### Added
- **Venue Notes & Curator Intelligence (`src/db_manager.py`)**: Added `venue_notes` database table, schema migrations, and methods `add_venue_note()` and `get_venue_notes()` enabling curators to record private, timestamped notes regarding sound specs, door policies, and promoter intelligence.
- **Venue Notes API (`src/dashboard/app.py`)**: Added `/venue/<venue_id>/notes` GET and POST endpoints for retrieving and recording annotations.
- **Curator Notes UI (`src/dashboard/templates/venue_detail.html`)**: Added an interactive "Curator Annotations & Scene Intelligence" card with submission form and chronological note feed on venue detail pages.
- **Venue Notes Test Suite (`tests/test_venue_notes.py`)**: Added unit and integration tests verifying note insertion, retrieval, and API responses.

## [1.1.82] - 2026-11-05

### Added
- **Detroit Underground Vibe Calibration (`src/ai_engine.py`)**: Calibrated AI vibe scoring prompts with strict 6.5 minimum threshold, dedicated evaluation for acoustic performance (Funktion-One, Void Acoustics, d&b audiotechnik, Danley), underground corridors (Russell Industrial, Eastern Market, Hamtramck, Milwaukee Junction), and rejection criteria for mainstream VIP/bottle service clubs.
- **Float-Precision Vibe Threshold Support**: Enabled decimal-precision vibe thresholds across `database/config.json`, `src/config_manager.py`, and dashboard settings views.
- **Midwest-Toronto Circuit Optimizer (`src/tour_planner.py`)**: Enhanced tour routing logic to anchor circuits in Detroit, link regional Midwest stops (Ferndale, Ann Arbor, Grand Rapids, Chicago, Cleveland, Columbus), and integrate Toronto with international touring considerations (Ambassador Bridge / Detroit-Windsor Tunnel crossings, ATA Carnet / gear manifests, USD/CAD dual currency notes).
- **Tour Routing Test Suite (`tests/test_circuit_optimizer.py`)**: Added dedicated integration tests for Detroit-anchored routing, cross-border itinerary annotations, and strict 6.5 vibe threshold filtering.

## [1.1.81] - 2026-11-05

### Added
- **Pipeline Activity Digest Generator (`src/digest_generator.py`)**: Built `DigestGenerator` module to aggregate outreach metrics over customizable rolling windows (daily, weekly, monthly), including qualified leads, sent pitches, inbound replies by sentiment, booked venues, and AI token consumption.
- **HTML & Plain Text Digest Rendering**: Formats activity digests with styled HTML badges and responsive layout for email clients, alongside plain text fallbacks.
- **Dashboard Digest Preview & Dispatch (`/preview_digest`, `/send_digest`)**: Added preview and instant send endpoints in `src/dashboard/app.py`.
- **Interactive Digest Modal (`index.html`)**: Added modal with dynamic time window selector, recipient email override, and embedded live iframe preview.
- **Digest Generator Test Suite (`tests/test_digest_generator.py`)**: Added unit and integration tests verifying metric calculation, message formatting, mailer dispatching, and dashboard routes.

## [1.1.80] - 2026-11-04

### Added
- **Venue Comparison View (`/compare_venues`)**: Added endpoint in `src/dashboard/app.py` returning side-by-side venue comparative metadata (vibe score, traits, capacity, venue type, status, ratings).
- **Interactive Comparison Modal (`index.html`)**: Added comparison modal and multi-select trigger in the unified dashboard pipeline view.
- **Venue Comparison Test Suite (`tests/test_venue_comparison.py`)**: Added automated unit and integration tests verifying comparison data extraction and traits formatting.

## [1.1.79] - 2026-11-04

### Added
- **Asynchronous Bulk Lead Actions (`/bulk_action`)**: Added threaded batch actions in `src/dashboard/app.py` for batch approvals, rejections, and AI requalifications without blocking UI response times.
- **Interactive Batch Selection UI (`index.html`)**: Added Select All checkbox, item check triggers, and Batch Approve / Batch Reject / Batch Re-score buttons in the outreach pipeline views.
- **Automated Bulk Action Tests (`tests/test_bulk_actions.py`)**: Added integration test coverage for batch approvals, status updates, email dispatching, and parameter validation.

## [1.1.78] - 2026-11-04

### Added
- **Unified Single-Page Command Center (`src/dashboard/templates/index.html`)**: Fully consolidated all disparate dashboard pages (`/map`, `/analytics`, `/settings`, `/system`, `/sources`, `/pending_qualification`, `/history`, `/booked`, `/dm_queue`, `/pending_follow_ups`) into a single priority-ranked interface with master tabs, quick-action header buttons, global KPI cards, and tooltips.
- **Desktop System Tray Companion (`src/dashboard/tray.py`, `tray.sh`)**: Built desktop tray companion with options to monitor status, open dashboard, trigger outreach pipeline, fetch inbox replies, execute repository sync protocol, and gracefully stop/quit servers. Added headless terminal/CLI daemon fallback for environments without graphical displays.
- **Graceful Server Shutdown Endpoint (`/shutdown`)**: Added secure endpoint in `app.py` enabling operator and companion process termination with testing environment safety guards.
- **Unified Dashboard Integration Test Suite (`tests/test_unified_dashboard.py`)**: Added full automated testing suite verifying master tab parameters, backward-compatible route rendering, tray companion handlers, and shutdown endpoint.

### Changed
- **Repository Hygiene Hardening**: Added `MagicMock/`, `.pytest_cache/`, and coverage artifacts to `.gitignore` to prevent version control pollution during test runs.

## [1.1.77] - 2026-07-13

### Added

- **Repository Synchronization**: Executed EXECUTIVE PROTOCOL — fetched all remotes, fast-forwarded all 5 local feature branches (10 refs), cleaned up stale `temp-feature-merge` branch, verified all branches at identical commit.
- **Documentation Reconciliation**: Reconstructed missing CHANGELOG entries v1.1.69–v1.1.76. Updated ROADMAP, TODO, and HANDOFF.

## [1.1.76] - 2026-07-13

### Added

- **Tour Routing & Proximity Clustering Module**: Initialized dedicated component for automated geographic tour planning.
- **A/B Analytics Dashboard**: New `ab_testing.html` template with live variant performance and significance indicators.

## [1.1.75] - 2026-07-12

### Added

- **DM Queue Dashboard Integration**: Exposed IG/FB DM queue and live A/B analytics on the main HITL dashboard.
- **Multi-City Outreach Scaling**: Pipeline handles concurrent DM/email outreach across all circuit cities without state corruption.

## [1.1.74] - 2026-07-12

### Added

- **Phase 50: Follow-up & Sentiment Engine**: Begun implementation — automated follow-up triggers for positive DM leads.
- **IG DM Context Propagation**: `is_dm` flag propagated through `main.py` pipeline; Instagram handles used when email missing.
- **DM Formatting**: Casual DM formatting triggered via `is_dm` flag in AIEngine, verified by unit tests.

### Fixed

- **Database Locking**: Resolved SQLite `OperationalError: database is locked` in `OutreachEngine`/`DatabaseManager` concurrent write paths.

## [1.1.73] - 2026-07-11

### Added

- **IG DM Ingestion Pipeline**: Instagram DM ingestion alongside email `inbox_monitor.py` pipeline.
- **DM Pitch Logic**: IG/FB DM templates hooked into AI pitch generation via `is_dm` flag.
- **DB Concurrency**: Refactored write paths to reduce lock contention.

## [1.1.72] - 2026-07-10

### Added

- **Instagram DM Ingestion**: Full DM ingestion for automated social media venue response handling.
- **Multi-City Scaling**: Concurrent outreach across all 10 circuit cities without throttling conflicts.

## [1.1.71] - 2026-07-09

### Added

- **A/B Testing Statistical Significance Calculator**: Halts variant tests at 95% confidence. Completes Phase 42 Outreach Intelligence suite.
- **A/B Testing Dashboard**: `ab_testing.html` with live experiment monitoring, variant comparison, significance indicators.

## [1.1.70] - 2026-07-09

### Added

- **"Add Venue Manually" Form**: Dashboard form for manual venue entry.
- **Manual Venue Test Suite**: `tests/test_manual_venue.py`.

## [1.1.69] - 2026-07-08

### Added

- **"Do Not Contact" List**: Per-lead and per-venue DNC mechanism. Venues requesting no contact are permanently blocked.
- **Alpha Banner**: Added "UNDER CONSTRUCTION — ALPHA STATE" to README.

## [1.1.64] - 2026-06-19

### Added

- **UI Refinement**: Implemented dashboard notifications for new replies requiring attention, including a navbar badge and individual "Needs Attention" tags with dismiss buttons in the History view.

## [1.1.63] - 2026-06-12

### Added

- **Phase 48: Usage Transparency & Inbox Reliability**: Finalized integration of token usage tracking and bounce detection.
- **Phase 47: Multi-Artist Collective Architecture**: Completed the transition to a collective model with per-lead artist assignment.
- **Lead Export**: Added CSV export functionality for leads and contacts.
- **Architecture Review**: Conducted a full src/ audit, confirming 100% logic coverage and zero remaining TODOs.
- **Repository Synchronization**: Executed the Executive Protocol for Repository Synchronization, reconciling all legacy feature branches into `main`.

### Fixed

- **RA Enrichment Regression**: Resolved double-initialization of retry logic in `ResidentAdvisorWebScraper`.
- **System Stability**: Re-verified 100% pass rate on Master Integrity Suite (84 tests) post-synchronization.
- **Staging Deployment**: Successfully executed staging deployment protocol with 100% test pass rate and stability verification.

## [1.1.62] - 2026-06-11

### Added

- **AI Token Usage Tracking**: Implemented automated tracking and logging of OpenAI token usage (prompt, completion, total) for all AI calls.
- **AI Usage Dashboard**: Added a new visualization in the System dashboard showing 7-day token consumption per model.
- **Unmatched Reply Management**: Implemented an "Unmatched Replies" system to capture and store incoming emails that cannot be automatically linked to a lead.
- **Manual Match UI**: Added a UI in the History view for manually assigning unmatched replies to leads.
- **SMTP Bounce Detection**: Integrated automated detection for delivery failure notifications (bounces), with automatic lead status updates to 'BOUNCED'.
- **Verification Suites**: Added `tests/test_ai_usage.py` and `tests/test_bounce_detection.py` to the Master Integrity Suite.

## [1.1.58] - 2026-06-10

### Added

- **Phase 46: Advanced Reporting & Scene Analytics**: Enhanced `AnalyticsEngine` with conversion funnel logic (Discovered -> Qualified -> Pitched -> Replied -> Booked).
- **Scene Health KPIs**: Implemented new metrics including Response Rate, Booking Rate, and Interest Rate.
- **Venue Warmth Scoring**: Implemented a dynamic "warmth" score (0-100) based on interaction recency and sentiment to prioritize lead follow-ups.
- **Analytics Dashboard UI**: Added a dedicated Analytics Reporting view to the dashboard with funnel visualizations and KPI cards.
- **Phase Verification Suite**: Created `tests/test_analytics_reporting.py` and `verify_phase46.py` to ensure reporting accuracy.

## [1.1.57] - 2026-06-10

### Added

- **Staging Quality Gate**: Updated `deploy_staging.sh` to require `PERFORMANCE.md` verification, mirroring the production deployment protocol.

## [1.1.56] - 2026-06-10

### Added

- **Master Branch Reconciliation**: Successfully merged all active feature branches into `main` using the `ours` strategy to preserve the advanced system state while maintaining history.

## [1.1.55] - 2026-06-09

### Added

- **CI/CD Performance Integration**: Updated `deploy_production.sh` to mandate verification of the technical performance report (`PERFORMANCE.md`) before deployment.
- **QA Sign-off Protocol**: Created `src/qa_signoff.py` and integrated it into the production deployment pipeline to ensure a final human-auditable quality gate.

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
- **Stability Milestone**: Achieved 100% pipeline stability documented in `PERFORMANCE.md`.

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
