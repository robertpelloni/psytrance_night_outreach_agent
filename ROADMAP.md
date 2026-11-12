# ROADMAP

## Completed Phases

### Phase 1: Core Infrastructure & Scouting

- [x] Database Schema Implementation (SQLite)
- [x] Google Maps Scraping & Enrichment
- [x] Basic Contact Mining (Web & Socials)
- [x] CI/CD Repository Synchronization Protocol
- [x] Data Integrity & Unique Constraints
- [x] AI-Driven Real-time Scraper Generation
- [x] Automated Sync Logic Testing
- [x] End-to-End Unified Protocol Execution
- [x] AI-Powered Merge Conflict Resolution
- [x] Autonomous Development Cycle Integration
- [x] Production Milestone Integration (v1.0.0)

### Phase 2: AI Qualification & Personalization

- [x] LLM Vibe Check (Suitability Scoring)
- [x] Bespoke Pitch Generation
- [x] Prompt Engineering for Psytrance Context

### Phase 3: HITL Dashboard

- [x] Web UI for Lead Review
- [x] Approval Workflow
- [x] Edit & Regenerate Pitch Functionality
- [x] Lead History View

### Phase 4: Outreach Execution

- [x] Email Dispatch Integration (SMTP)
- [x] Social Media Outreach Assistance
- [x] Analytics & Tracking

### Phase 5: Configuration & Branding

- [x] Centralized Project Configuration (Cities, Genres)
- [x] Branding Integration (EPK, Mix Links)
- [x] Web UI for Settings Management

### Phase 6–12: Robustness, Scaling, Monitoring (v1.0.2–v1.1.0)

- [x] Proxy/UA Rotation, Auto-Approval Engine, Follow-up Engine
- [x] Multi-City Resume, Smoke Testing, Staging Deployment
- [x] Validated Push Protocol, Sentiment Analysis, Health Monitoring
- [x] Root Script Consolidation, Cross-Branch Reconciliation

### Phase 13–23: Integration, CI/CD, Global Sync (v1.1.1–v1.1.26)

- [x] E2E Pipeline Verification, Production Pilot, Tiered Deployment
- [x] Cross-Branch Consistency, Remote Sync, Multi-Branch Stress Testing
- [x] Trait Extraction, Geographic Mapping & Heatmaps
- [x] Tour Routing, Proximity Clustering, Media Matching
- [x] Version Auditor, Executive Sync Protocol

### Phase 24–35: Intelligence & Vision (v1.1.27–v1.1.40)

- [x] Instagram Scraper, Social Context Integration
- [x] Outreach Predictor, Success Probability
- [x] Cluster Outreach, RA Enrichment Scraper
- [x] Reply Negotiation, Genre Dynamic Adaptation
- [x] Multi-Genre Discovery, Geocoding Precision
- [x] Vision-Enriched Qualification (GPT-4o-vision)

### Phase 36: Detroit-Focus Refoundation (v1.1.44)

- [x] Retarget all cities to Detroit + Midwest circuit
- [x] Add Detroit neighborhood-aware search queries
- [x] Add artist identity system (artist_name, collective_name, home_city)
- [x] Rewrite AI prompts with Detroit scene context
- [x] Lower vibe threshold to 6 (cast wider net in untapped market)
- [x] Add Detroit-specific trait extraction (detroit_relevance)
- [x] Rewrite main.py with multi-query neighborhood search strategy
- [x] Refactor pipeline into modular qualify_and_pitch function
- [x] Update ConfigManager with full Detroit config defaults

### Phase 37: Real-World Scraper Hardening (v1.1.45)

- [x] Add retry logic with exponential backoff to `GoogleMapsPlaywrightScraper`
- [x] Implement per-venue try/catch isolation in `main.py`
- [x] Validate scraper output (reject empty names/missing cities)
- [x] Add rate limiting between scraper calls
- [x] Implement pipeline "dry run" mode

### Phase 38: Dynamic Proxy Rotation & Multi-Scraper Hardening (v1.1.46-v1.1.47)

- [x] Implement health tracking in `ProxyRotator` (success/fail counts)
- [x] Add exponential backoff blacklisting for failing proxies
- [x] Integrate feedback loop from scrapers (success/failure reporting)
- [x] Apply production hardening (retries + isolation) to RA and Instagram scrapers
- [x] Optimized discovery loop to separate query-based vs. city-based scrapers (v1.1.48)
- [x] Verified 100% stability across Master Integrity Suite (v1.1.63 Report)
- [x] Conducted v1.1.63 Performance Review (See [PERFORMANCE.md](PERFORMANCE.md))

### Phase 39: Email Inbox Integration (v1.1.49)

- [x] Implement IMAP inbox polling (`src/inbox_monitor.py`)
- [x] Match incoming emails to leads by sender address or venue name
- [x] Auto-route matched emails through `SentimentAnalyzer`
- [x] Add "Fetch New Replies" button to the HITL Dashboard (v1.1.49)
- [x] Poll on configurable interval (integrated into main pipeline cycle)
- [x] Handle bounce emails: detect SMTP bounces and mark leads as BOUNCED (v1.1.62)

### Phase 40: Pipeline Scheduling & Cycle Management (v1.1.50)

- [x] Integrate APScheduler into the dashboard app
- [x] Add configurable schedule (default: weekly)
- [x] Implement `db.reset_city_cycle(city)` to allow re-running discovery
- [x] Add a "Reset All Cycles" button on the dashboard
- [x] Add pipeline run history to the database and dashboard view

### Phase 41: Settings & Dashboard Completeness (v1.1.51)

- [x] Add Artist Identity section to Settings UI
- [x] Add Media Library management to Settings UI
- [x] Add Detroit Search Queries and Neighborhoods editor to Settings UI
- [x] Add auto_approve_threshold, follow_up_days, max_follow_ups to Settings UI
- [x] Add "PENDING_QUALIFICATION" view to dashboard
- [x] Add venue detail page with full venue info and reply history
- [x] Fix map default center to Detroit (42.3314, -83.0458)
- [x] Add "Re-qualify" button on PENDING_QUALIFICATION leads

### Phase 42: Outreach Intelligence & Safety (v1.1.51)

- [x] Add daily outreach throttle (max 10 emails/day)
- [x] Add configurable delay between dispatches (5 minutes)
- [x] Add OpenAI token budget tracker (v1.1.62)
- [x] Add per-run and per-day OpenAI token budget alerts (v1.1.65)
- [x] Add pitch subject line generation via AI (v1.1.68)
- [x] Add "Do Not Contact" list for venues (v1.1.69)
- [x] Add A/B testing statistical significance calculator (v1.1.71)
- [ ] Add email open/click tracking via tracking pixel or link wrapper

### Phase 43: Data Model & Persistence Improvements (v1.1.52)

- [x] Add address, phone, type, capacity, and neighborhood to `venues` table
- [x] Add migration system for safe schema upgrades in `DatabaseManager`
- [x] Add `pipeline_runs` table for tracking run history

### Phase 44: Detroit Venue Seed & Community Intelligence (v1.1.51)

- [x] Create `database/detroit_venues_seed.json` with 30 seed venues
- [x] Add seed import command: `python main.py --seed`
- [x] Add "Add Venue Manually" form to dashboard
- [x] Add venue notes/annotations system (v1.1.83)
- [x] Deep integration of curator annotations into AI pitch generation and vibe checking (v1.1.84)

### Phase 45: Reply Automation & Negotiation Engine (v1.1.54)

- [x] Add auto-response for OOO replies (v1.1.54)
- [x] Add negotiation state machine (INITIAL → REPLIED → NEGOTIATING → BOOKED / LOST)
- [x] Add "Mark as Booked" workflow on dashboard
- [x] Add booking tracker view for BOOKED status leads

### Phase 46: Reporting & Scene Analytics (v1.1.58)

- [x] Add conversion funnel visualization (Discovered → Qualified → Pitched → Replied → Booked)
- [x] Add "Scene Health" KPIs (Response, Interest, and Booking Rates)
- [x] Add venue "warmth" score based on interaction recency and sentiment
- [x] Add venue outreach timeline visualization (v1.1.63)

### Phase 47: Multi-Artist & Collective Support (v1.1.62)

- [x] Add artist profiles table (bio, links, rate card)
- [x] Allow pitches to reference specific artists from the collective
- [x] Add "billed artist" field to leads and per-artist analytics (v1.1.62)

### Phase 48: Usage Transparency & Inbox Reliability (v1.1.62)

- [x] Log OpenAI token usage (prompt, completion, total) per API call (v1.1.62)
- [x] Add "AI Usage (7d)" visualization to the System dashboard (v1.1.62)
- [x] Implement automated SMTP bounce detection (v1.1.62)
- [x] Implement manual matching for unmatched replies (v1.1.62)

---

## Upcoming Phases

### Phase 49: Social Media Automation (v1.1.65)

Expand beyond email into automated social media outreach assistance.

- [x] Implement Instagram/Facebook DM assistance and ingestion
- [x] Add dashboard notification for new replies requiring attention (v1.1.64)
- [x] Implement per-run and per-day token budget alerts
- [x] Refine "Pending Qualification" view with bulk approval actions (v1.1.79)
- [x] Add venue comparison view (side-by-side) (v1.1.80)

---

### Phase 50: Automated Follow-up & Sentiment Engine

Expand reply parsing logic to deeply integrate sentiment and trigger automatic follow-ups.

- [x] Implement sentiment analysis for incoming DM responses to auto-tag lead warmth
- [x] Build automated follow-up triggers for positive DM leads (low-friction guidelines)
- [x] Add DM lead tracking visibility to the HITL dashboard

---

### Phase 51: Unified Command Center & Desktop System Tray Companion (v1.1.78)

Consolidate fragmented dashboard subpages and provide system daemon management.

- [x] Consolidate map, analytics, settings, sources, queues, and system health into a single unified dashboard (`index.html`)
- [x] Implement desktop companion (`tray.py` and `tray.sh`) with headless CLI fallback
- [x] Add graceful `/shutdown` server management endpoint
- [x] Add automated test suite for unified dashboard architecture (`tests/test_unified_dashboard.py`)

---

### Phase 52: Pipeline Activity Digests & Comparison Analytics (v1.1.80 - v1.1.81)

Operational intelligence, side-by-side venue matrix evaluation, and periodic email summaries.

- [x] Implement side-by-side venue matrix comparison endpoint and interactive modal (`/compare_venues`)
- [x] Implement pipeline digest generator (`DigestGenerator` in `src/digest_generator.py`)
- [x] Add dashboard preview and instant dispatch endpoints (`/preview_digest`, `/send_digest`)
- [x] Integrate pipeline activity digest modal into unified dashboard Analytics tab
- [x] Add automated test suite for digest generation and dashboard integration (`tests/test_digest_generator.py`)

---

### Phase 53: Detroit Vibe Calibration & Midwest-Toronto Circuit Optimization (v1.1.82)

Refine underground acoustic vibe checks and optimize multi-city touring circuits spanning Detroit to Toronto.

- [x] Calibrate AI vibe check prompts with strict 6.5 minimum threshold and sound system evaluation (Funktion-One, Void, d&b)
- [x] Support decimal-precision vibe thresholds across configuration schema and dashboard settings UI
- [x] Anchor multi-city tour routing to Detroit with proximity connections across the Midwest corridor (Chicago, Grand Rapids, Columbus, Cleveland) and Toronto
- [x] Inject international touring logistics (Ambassador Bridge / Detroit-Windsor Tunnel crossings, ATA Carnet / gear declaration, USD/CAD currency guidance)
- [x] Add automated test suite for tour planning and cross-border circuit optimization (`tests/test_circuit_optimizer.py`)

---

### Phase 54: Curator Intelligence & Venue Field Notes (v1.1.83 - v1.1.84)

Internal note-taking and sound engineer/curator intelligence embedded into AI qualification and pitch generation.

- [x] Implement `venue_notes` database schema and data manager methods (`src/db_manager.py`)
- [x] Expose REST endpoints for note management (`/venue/<id>/notes`)
- [x] Add curator intelligence timeline and interactive submission form to venue detail views
- [x] Wire curator notes into `AIEngine.generate_pitch()` and `AIEngine.vibe_check()` for context-aware pitch generation
- [x] Add automated test suites for note storage and pitch integration (`tests/test_venue_notes.py`, `tests/test_notes_in_pitch.py`)

---

### Phase 55: DBSCAN Dynamic Density & Transit Clustering Metrics (v1.1.85)

Algorithmic cluster geometry calculation and inter-city corridor transit estimation.

- [x] Calculate cluster bounding-box radius (`cluster_radius_km`) and estimated transit drive times (`est_intercity_drive_hrs`) in `AnalyticsEngine.get_venue_clusters()`
- [x] Display corridor density badges, transit drive times, and quick-filter buttons in Geographic Map & Circuit Optimizer dashboard tab
- [x] Add automated test suite for dynamic clustering and perimeter transit metrics (`tests/test_advanced_clustering.py`)

---

### Phase 56: Collaborative Filtering & Alternate Venue Recommendation (v1.1.86)

Algorithmic recommendation engine suggesting high-affinity sibling venues when a prospect is rejected or stalled.

- [x] Implement `RecommendationEngine` in `src/recommendation_engine.py` using acoustic trait overlap, Haversine distance decay, capacity matching, and lead vibe scoring
- [x] Expose `/recommend_venues/<venue_id>` endpoint with limit and minimum score filtering
- [x] Integrate interactive "Alternate Venues" recommendation modal in dashboard queues and venue detail pages
- [x] Add unit and integration tests verifying collaborative filtering logic (`tests/test_recommendation_engine.py`)

---

### Phase 57: Eventbrite & Nightlife Aggregator Discovery (v1.1.87)

Automated discovery of underground nightlife and electronic music spaces from Eventbrite listings.

- [x] Implement `EventbriteWebScraper` in `src/scrapers/eventbrite.py` supporting schema.org JSON-LD and card fallbacks
- [x] Dynamically load Eventbrite scraper in `main.py` and register it in dashboard Scraper Sources tab
- [x] Add unit and integration tests verifying Eventbrite parsing and rate-limit backoff (`tests/test_eventbrite_scraper.py`)

---

### Phase 58: Email Engagement & Interaction Tracking (v1.1.88)

1x1 pixel open tracking and hyperlink redirection for empirical interest analysis.

- [x] Implement `email_tracking_events` database schema and data manager methods in `src/db_manager.py`
- [x] Enhance `Mailer` to inject 1x1 transparent tracking pixels and wrap EPK/audio links
- [x] Expose `/track/open/<lead_id>.gif` and `/track/click/<lead_id>` in `src/dashboard/app.py`
- [x] Add Email Engagement KPI strip to Analytics tab and lead engagement timeline to venue dossier pages
- [x] Add automated test suite for tracking event recording and redirects (`tests/test_email_tracking.py`)

---

### Phase 59: High-Precision Address Geocoding & Reverse Parsing (v1.1.89)

Progressive multi-tier address geocoding and reverse parsing for precise venue mapping and cluster transit computation.

- [x] Enhance `GeocodingUtility.geocode_venue` and `parse_and_enrich_venue_address` with progressive query tiers (`Venue + Address + City`, `Address + City`, `Venue + City`, GPT-4o fallback)
- [x] Extract normalized street address, postal code, and neighborhood from Nominatim address structures
- [x] Add `update_venue_address_details` in `DatabaseManager` for atomic spatial and neighborhood updates
- [x] Expose `POST /geocode_venue/<venue_id>` and `POST /geocode_all_unlocated` in `src/dashboard/app.py`
- [x] Surface "Geocode Missing" trigger in Geographic Map view and GPS precision status in venue dossiers
- [x] Add automated unit and integration tests (`tests/test_geocoding_enhanced.py`)

---

### Phase 60: Meetup Community & Event Scraper (v1.1.90)

Automated discovery of underground electronic gatherings, music communities, and non-commercial event venues via Meetup.

- [x] Implement `MeetupWebScraper` in `src/scrapers/meetup.py` with schema.org JSON-LD and HTML card parsing
- [x] Integrate proxy and user-agent rotation with rate-limit backoff resilience
- [x] Wire into dynamic scraper loader (`main.py`) and Scraper Sources tab in Unified Command Center
- [x] Add unit and integration test suite (`tests/test_meetup_scraper.py`)

---

### Phase 61: User Onboarding Tour & In-App Feedback Mechanism (v1.1.91)

Interactive multi-step walkthrough tour for first-time operators and in-app feedback collection for community curators.

- [x] Implement `operator_feedback` table and database persistence methods (`record_operator_feedback`, `get_operator_feedback`)
- [x] Create in-app Feedback modal and submission endpoints (`POST /submit_feedback`, `GET /api/feedback`)
- [x] Design interactive 5-step onboarding walkthrough (`#onboardingTourModal`) navigating through pipeline queues, circuit routing, artist dossiers, scraper sources, and system operations
- [x] Embed operator feedback history table in the System Health tab of the Unified Command Center
- [x] Add unit and integration test suite (`tests/test_feedback_and_onboarding.py`)

---

### Phase 62: Visual Aesthetic Vibe Scoring & GPT-4o-Vision Integration (v1.1.92)

Multimodal aesthetic qualification utilizing GPT-4o-vision to evaluate raw warehouse vibe, stage architecture, lighting rigs, and subterranean dancefloors.

- [x] Extend `venues` schema with `visual_vibe_score INTEGER` and dynamic migrations in `DatabaseManager`
- [x] Propagate `visual_vibe_score` from `AIEngine.analyze_visual_vibe()` through `main.py` pipeline into database persistence
- [x] Add on-demand `/analyze_venue_visuals/<venue_id>` endpoint for instantaneous curator re-analysis
- [x] Integrate Visual Vibe badge (1-10 aesthetic alignment) and aesthetic breakdown card in venue dossier UI (`venue_detail.html`)
- [x] Add automated unit and integration test suite (`tests/test_visual_vibe_qualification.py`)

---

### Phase 63: Operator Feedback Triage & Resolution Workflow (v1.1.93)

Comprehensive triage lifecycle management for collective curator suggestions and bug reports.

- [x] Extend `operator_feedback` table with `status TEXT DEFAULT 'PENDING'` (`PENDING`, `IN_REVIEW`, `RESOLVED`) and automatic migrations
- [x] Implement status update and status filtering methods in `DatabaseManager` (`update_operator_feedback_status`, `get_operator_feedback`)
- [x] Expose `POST /update_feedback_status/<feedback_id>` in `src/dashboard/app.py`
- [x] Integrate inline triage action buttons (`Review`, `Resolve`, `Re-open`) and status badges in Unified Command Center (`index.html`)
- [x] Add automated unit and integration test suite (`tests/test_feedback_and_onboarding.py`)

---

### Phase 64: Command Center Automated Test Suite & Map Visual Verification (v1.1.94)

Comprehensive verification and automated testing of unified dashboard architecture, interactive modals, and mapping controls.

- [x] Expand `tests/test_unified_dashboard.py` covering all core modals (`#onboardingTourModal`, `#feedbackModal`, `#compareModal`, `#digestModal`, `#recModal`, `#addVenueModal`)
- [x] Verify feedback triage state indicators and triage action endpoints
- [x] Verify geocoding missing venues endpoints and email engagement metrics strip
- [x] Conduct Playwright visual layout inspection and screenshot verification of consolidated Map tab

---

### Phase 65: Tour Routing & Transit Corridor Analytics (v1.1.95)

Hierarchical corridor clustering, circuit transit logistics, carbon estimation, and media asset matching.

- [x] Implement hierarchical agglomerative clustering in `AnalyticsEngine.get_venue_clusters(method='hierarchical')`
- [x] Add circuit transit logistics calculation (`compute_circuit_logistics()`) in `TourPlanner` (transit km, drive hrs, rest days, CO2 footprint)
- [x] Expose `POST /api/tour/simulate_circuit` and enriched `GET /plan_circuit` in `src/dashboard/app.py`
- [x] Wire transit metrics strip, clustering algorithm controls, and paired media assets into `#tourModal` in `src/dashboard/templates/index.html`
- [x] Add unit and integration tests (`tests/test_tour_routing_enhanced.py`)

---

### Phase 66: Collaborative Filtering Midwest Acoustic Weighting & Contingency Pitching (v1.1.96)

Audio architecture weighting for sound systems (Funktion-One, Void, Danley, d&b, PK Sound) and automated contingency pitch generation for alternative venues.

- [x] Enhance `RecommendationEngine` with explicit acoustic rig scoring and composite affinity rebalancing
- [x] Implement `generate_contingency_pitch()` in `RecommendationEngine` supporting turnkey regional residency and touring proposals
- [x] Add `POST /api/recommendations/pitch/<target_venue_id>/<alt_venue_id>` endpoint in `src/dashboard/app.py`
- [x] Integrate inline "Draft Pitch" triggers and live contingency pitch preview box into `#recModal` in `src/dashboard/templates/index.html`
- [x] Add automated unit and integration tests (`tests/test_recommendation_contingency.py`)

---

### Phase 67: Outreach Timing Matrix & Response Velocity Analytics (v1.1.97)

Temporal engagement profiling across days of the week and hours of the day to detect optimal booking agent dispatch windows.

- [x] Implement 7x24 temporal aggregation matrix in `AnalyticsEngine.get_activity_heatmap()`
- [x] Compute peak promoter engagement slots with daytime/evening descriptions
- [x] Expose `GET /api/analytics/activity_heatmap` REST API endpoint
- [x] Integrate interactive 7x24 heatmap table with density shading and tooltips in the Analytics tab
- [x] Add unit and integration tests (`tests/test_analytics_heatmap.py`)

---

### Phase 68: Venue Touring Dossier JSON & Itinerary Export (v1.1.98)

Standardized JSON and CSV export endpoints and interface controls for booking agency and tour management interoperability.

- [x] Implement `AnalyticsEngine.export_leads_json()` and `AnalyticsEngine.export_circuit_itinerary_json()`
- [x] Support individual venue objects in `TourPlanner.compute_circuit_logistics()`
- [x] Expose `GET /export_leads_json` and `POST /export_circuit_itinerary` endpoints
- [x] Integrate "Export JSON" action on the conversion funnel card and "Export Itinerary JSON" inside `#tourModal`
- [x] Add unit and integration tests (`tests/test_itinerary_export.py`)

---

### Phase 69: Unified Venue Notes & Curator Scene Intelligence (v1.1.99)

In-situ venue scene intelligence, sound rig notes, and confidential promoter relationship logging directly within the unified dashboard queues.

- [x] Implement interactive `#venueNotesModal` in `src/dashboard/templates/index.html` with real-time chronological intelligence feed
- [x] Add quick-action `📝 Notes` buttons across pipeline cards to inspect and append confidential field notes
- [x] Verify `POST /venue/<venue_id>/notes` and `GET /venue/<venue_id>/notes` dual-support for JSON AJAX payloads and standard form requests
- [x] Validate frontend via Playwright script capturing interactive modal entry and timeline updates
- [x] Add unit and integration test suite (`tests/test_dashboard_venue_notes.py`)

---

### Phase 70: Spherical K-Means Tour Clustering & Enhanced Media Matching (v1.2.0)

Partition-based regional tour clustering using spherical geometry and contextual media pack pairing.

- [x] Implement Spherical K-Means / geographic Lloyd's partitioning in `AnalyticsEngine.get_venue_clusters(method='kmeans')`
- [x] Dynamic Haversine centroid updates and cluster radius computation for balanced regional hubs
- [x] Enhance `TourPlanner.compute_circuit_logistics()` with media asset category classification (`Core Press`, `Live Audio`, `forest`, `ambient`)
- [x] Wire K-Means clustering selector and styled media library badges into `#tourModal` in `src/dashboard/templates/index.html`
- [x] Validate modal frontend changes and clustering recalculation via Playwright script
- [x] Add comprehensive unit and integration test suite (`tests/test_kmeans_clustering.py`)

---

### Phase 71: Facebook Events Discovery Scraper (v1.2.1)

Public Facebook events scouting for underground gatherings and non-commercial music venues.

- [x] Implement `FacebookEventsWebScraper` in `src/scrapers/facebook_events.py` inheriting from `BaseScraper`
- [x] Schema.org JSON-LD event parsing and fallback HTML card extraction
- [x] Proxy and User-Agent rotation with rate-limit retry resilience
- [x] Dynamic loader integration into `main.py` query-based scrapers
- [x] Real-time scraper status indicator in Scraper Sources dashboard tab
- [x] Add comprehensive test suite (`tests/test_facebook_scraper.py`)

## Backlog / Future Ideas

See [IDEAS.md](IDEAS.md) for unconstrained future feature ideas.

### Phase 4 Outreach Execution Enhancements
- [x] Integrate SMTP logic with `.env` loading and establish a dry-run test suite.
- [x] Hook IG/FB DM templates directly into the `AIEngine` pitch generator and trigger simulated DM execution.
- [x] Fix concurrent database write locks during the primary outreach dispatch cycle.

### Phase 4 Outreach Execution Enhancements
- [x] Integrate A/B testing selection and IG DM pitch generation dynamically based on data availability in the primary qualification loop.
