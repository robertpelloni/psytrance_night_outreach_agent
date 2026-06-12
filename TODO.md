# TODO

## ✅ Completed

- [x] Initialize git repository structure
- [x] Create `schema.sql` for the database
- [x] Setup project structure (Python)
- [x] Implement Google Maps scraper (Playwright)
- [x] Implement Resident Advisor scraper
- [x] Implement Website contact extractor
- [x] Integrate LLM for vibe check
- [x] Integrate LLM for pitch generation
- [x] Create a simple web dashboard for review
- [x] Enhance dashboard with approval workflow
- [x] Implement SMTP email dispatch
- [x] Create User Manual (MANUAL.md)
- [x] Implement Proxy/UA Rotation
- [x] Add Dashboard History View
- [x] Add Database Tests
- [x] Add AI Engine Tests
- [x] Implement AI Scraper Generator
- [x] Implement Dynamic Scraper Loading
- [x] Add Source Management Dashboard
- [x] Implement Outreach Analytics
- [x] Add Social Media Helper (Clipboard DM)
- [x] Implement Dynamic Configuration Manager
- [x] Add Branding (EPK/Mix) Integration to AI
- [x] Create Settings Dashboard
- [x] Final Production Integration (v1.0.0)
- [x] Implement Proxy Rotation (v1.0.2)
- [x] Implement Outreach Engine for automated dispatch (v1.0.2)
- [x] Integrate Synchronization Protocol into CI Pipeline (Multi-Branch)
- [x] Implement Follow-up Engine (v1.0.3)
- [x] Implement Multi-City Resume Logic (v1.0.4)
- [x] Add Comprehensive Smoke Test (v1.0.4)
- [x] Deploy Staging Environment and CI Workflow
- [x] Harden Sync Protocol with internal validation (v1.0.7)
- [x] Implement Sentiment Analysis for Lead Replies (v1.0.8)
- [x] Implement Autonomous Health Monitoring (v1.0.9)
- [x] Reorganize and stabilize root script architecture (v1.1.0)
- [x] Implement End-to-End Autonomous Pipeline Integration Test (v1.1.1)
- [x] Create Live Connectivity Test Suite (v1.1.2)
- [x] Implement Production Pilot Script (v1.1.2)
- [x] Implement Tiered Production Deployment Workflow (v1.1.3)
- [x] Implement Cross-Branch Consistency Integration Test (v1.1.4)
- [x] Implement Real-time Remote Update Integration Test (v1.1.5)
- [x] Expand target city backlog to 15 global hubs (v1.1.7)
- [x] Integrate full Master Integrity Suite into CI (v1.1.7)
- [x] Implement Multi-Branch Stress Test and reporting (v1.1.8)
- [x] Visualize branch health matrix in Dashboard (v1.1.8)
- [x] Implement ReliabilityMonitor and Dashboard KPIs (v1.1.9)
- [x] Add automated branch pruning to sync protocol (v1.1.9)
- [x] Implement Staging Environment Validation Suite (v1.1.10)
- [x] Integrate health reporting into Staging Deployment (v1.1.10)
- [x] Implement Distributed Reconciliation Test (v1.1.11)
- [x] Add retry logic to push protocol (v1.1.11)
- [x] Implement AI-Driven Trait Extraction (v1.1.12)
- [x] Integrate Traits into HITL Dashboard (v1.1.12)
- [x] Persist Traits to Database (v1.1.12)
- [x] Implement Geographic Heatmap for Leads (v1.1.22)
- [x] Implement Proximity Clustering for Tour Planning (v1.1.23)
- [x] Add Status and Vibe filters to Map UI (v1.1.23)
- [x] Create AI Tour Routing Utility (v1.1.23)
- [x] Expand ConfigManager to support `media_library` (v1.1.24)
- [x] Update AIEngine to perform contextual media matching (v1.1.24)
- [x] Add "Dynamic Pitch Preview" to Dashboard (v1.1.24)
- [x] Harvest Git History into `version_audit_trail` (v1.1.25)
- [x] Verify Master Integrity Suite (40 tests) (v1.1.25)
- [x] Finalize v1.1.25 Milestone Documentation (v1.1.25)
- [x] Synchronize all local and remote feature branches (v1.1.26)
- [x] Verify architectural consolidation and audit trail (v1.1.26)
- [x] Implement `src/scrapers/instagram.py` (v1.1.27)
- [x] Refactor `ContactExtractor` to use live IG context (v1.1.27)
- [x] Refine AI vibe-check prompt with specific psytrance criteria (v1.1.27)
- [x] Create `src/outreach_predictor.py` (v1.1.28)
- [x] Display success probability on Dashboard (v1.1.28)
- [x] Verify predictor with unit tests (v1.1.28)
- [x] Implement `generate_cluster_pitch` in `TourPlanner` (v1.1.29)
- [x] Implement `dispatch_cluster_pitch` in `OutreachEngine` (v1.1.29)
- [x] Add Tour Modal to `map.html` (v1.1.29)
- [x] Refactor `ResidentAdvisorWebScraper` (v1.1.30)
- [x] Verify RA discovery with unit tests (v1.1.30)
- [x] Implement Resident Advisor Enrichment Scraper (v1.1.32)
- [x] Implement Intelligent Reply Negotiation & Draft Orchestration (v1.1.33)
- [x] Refactor system for Master Genre Dynamic Adaptation (v1.1.35)
- [x] Implement Multi-Genre Discovery Orchestration (v1.1.36)
- [x] Fix missing `re` import in `google_maps.py` (v1.1.37)
- [x] Implement `DB_PATH` environment isolation in `DatabaseManager` (v1.1.37)
- [x] Integrate Nominatim for precise geocoding (v1.1.38)
- [x] Implement Component-level Scraper Validation (v1.1.38)
- [x] Harden Sync Protocol branch filtering (v1.1.38)
- [x] Implement GPT-4o-vision analysis in AIEngine (v1.1.40)
- [x] Extract venue images in Google Maps and RA scrapers (v1.1.40)
- [x] Integrate vision analysis into qualification pipeline (v1.1.40)
- [x] Display venue images and visual analysis on HITL Dashboard (v1.1.40)
- [x] Verify Vision-Enriched Qualification with Master Integrity Suite (v1.1.40)
- [x] Retarget all cities to Detroit + Midwest circuit (v1.1.44)
- [x] Add Detroit neighborhood-aware search queries (v1.1.44)
- [x] Add artist identity system (artist_name, collective_name, home_city) (v1.1.44)
- [x] Rewrite AI prompts with Detroit scene context (v1.1.44)
- [x] Lower vibe threshold to 6 for wider net in untapped market (v1.1.44)
- [x] Add Detroit-specific trait extraction (detroit_relevance) (v1.1.44)
- [x] Rewrite main.py with multi-query neighborhood search strategy (v1.1.44)
- [x] Refactor pipeline into modular qualify_and_pitch function (v1.1.44)
- [x] Add retry logic with exponential backoff to `GoogleMapsPlaywrightScraper` (v1.1.45)
- [x] Implement per-venue try/catch isolation in `main.py` (v1.1.45)
- [x] Validate scraper output (reject empty names/missing cities) (v1.1.45)
- [x] Add rate limiting between scraper calls (v1.1.45)
- [x] Implement pipeline "dry run" mode (v1.1.45)
- [x] Implement Dynamic Proxy Rotation (v1.1.46)
- [x] Add health tracking to ProxyRotator (success/fail counts) (v1.1.46)
- [x] Integrate proxy feedback loop into all scrapers (v1.1.46)
- [x] Implement exponential backoff blacklisting for proxies (v1.1.46)
- [x] Apply production hardening (retries + isolation) to all scrapers (v1.1.47)
- [x] Optimize discovery orchestration (query vs city-wide) in main.py (v1.1.48)
- [x] Integrate proxy feedback into ContactExtractor.scrape_website (v1.1.48)
- [x] Implement website URL extraction in GoogleMapsPlaywrightScraper (v1.1.48)
- [x] Implement IMAP inbox polling in `src/inbox_monitor.py` (v1.1.49)
- [x] Implement dual-strategy lead matching (email + venue name) (v1.1.49)
- [x] Integrate `SentimentAnalyzer` for automated reply drafting (v1.1.49)
- [x] Add "Fetch New Replies" button to HITL Dashboard (v1.1.49)
- [x] Wired inbox polling into main pipeline orchestrator (v1.1.49)
- [x] Conducted v1.1.46 Performance Review (v1.1.58)
- [x] Arrange v1.1.46 Performance Review meeting with development team (v1.1.60)
- [x] Implement Advanced Reporting & Scene Analytics (Phase 46) (v1.1.58)
- [x] Add Conversion Funnel Visualization (v1.1.58)
- [x] Add Scene Health KPIs (Response, Interest, Booking Rates) (v1.1.58)
- [x] Add Venue Warmth Scoring (v1.1.58)
- [x] Conducted v1.1.46 Performance Review with QA team (v1.1.58)
- [x] Schedule v1.1.46 Performance Review with Operations team (v1.1.60)
- [x] Implement Unmatched Replies view and manual matching (v1.1.62)
- [x] Implement SMTP Bounce Detection and automatic lead marking (v1.1.62)
- [x] Implement AI Token Usage Tracking and Dashboard (v1.1.62)

---

## 🔴 Critical (Production Blockers)

These are the things that prevent the agent from being genuinely useful in the real world.

### Email Inbox Integration
- [ ] Add dashboard notification for new replies requiring attention
- [x] Add an "Unmatched Replies" view for emails that can't be auto-matched (v1.1.62)
- [x] Handle bounce emails: detect SMTP bounces and mark leads as BOUNCED (v1.1.62)

*IMAP polling is implemented (v1.1.49).*

### Scraper Reliability (Ongoing)
- [ ] Add Google Maps Places API as a reliable fallback when Playwright selectors break

### Pipeline Reset & Scheduling
- [x] Add `db.reset_city_cycle(city)` to allow re-running discovery for a city (v1.1.50)
- [x] Add "Reset All Cycles" button on dashboard (System tab) (v1.1.50)
- [x] Integrate APScheduler for automated pipeline runs (weekly) (v1.1.50)
- [x] Add pipeline run history table and dashboard view (v1.1.50)

*Automated scheduling and cycle management are operational (v1.1.50).*

---

## 🟡 High Priority (Needed for First Real Outreach Campaign)

### Settings & Dashboard Gaps
- [ ] Add Artist Identity section to Settings UI (artist_name, collective_name, home_city)
- [ ] Add Media Library management to Settings UI (add/edit/remove tagged media)
- [ ] Add Detroit Search Queries editor to Settings UI
- [ ] Add auto_approve_threshold, follow_up_days, max_follow_ups to Settings UI
- [ ] Fix map default center to Detroit (42.3314, -83.0458)
- [ ] Add "PENDING_QUALIFICATION" view to dashboard (venues below threshold)
- [ ] Add "Re-qualify" button on PENDING_QUALIFICATION leads

### Outreach Safety
- [x] Add daily outreach throttle (max N emails per day, default 10) to avoid spam flags (v1.1.50)
- [x] Add configurable delay between dispatches (e.g., 5 minutes between emails) (v1.1.50)
- [x] Add OpenAI token budget tracker (v1.1.62)
- [ ] Generate pitch subject lines via AI (currently hardcoded)
- [ ] Add "Do Not Contact" list for venues that asked to never be emailed again

### Detroit Bootstrap
- [ ] Create `database/detroit_venues_seed.json` with known Detroit venues (TV Lounge, Marble Bar, Spot Lite, El Club, New Dodge Lounge, etc.)
- [ ] Add seed import command: `python main.py --seed`
- [ ] Add "Add Venue Manually" form to dashboard
- [ ] Add venue notes/annotations system

### Data Model Gaps
- [x] Add `address` column to `venues` table (v1.1.52)
- [x] Add `phone` column to `venues` table (v1.1.52)
- [x] Add `venue_type` column (warehouse, club, bar, art_space, diy, lounge) (v1.1.52)
- [x] Add `capacity` column to `venues` table (v1.1.52)
- [x] Add `neighborhood` column to `venues` table (v1.1.52)
- [x] Add `source` column to `venues` (google_maps, resident_advisor, instagram, manual) (v1.1.52)
- [x] Add `discovered_at` timestamp to `venues` (v1.1.52)
- [ ] Add database indexes on frequently queried columns (city, pipeline_status, vibe_score)
- [x] Add `pipeline_runs` table for tracking run history (v1.1.52)
- [x] Add schema migration system for safe upgrades (v1.1.52)
- [x] Schedule v1.1.46 Performance Review meeting with dev team (v1.1.60)

---

## 🟢 Medium Priority (Post-Campaign Improvements)

### Reply Automation
- [x] Add auto-response for OOO replies (v1.1.54)
- [x] Add "rate inquiry" auto-draft with configurable rate card (v1.1.54)
- [x] Add negotiation state machine (INITIAL → REPLIED → NEGOTIATING → BOOKED / LOST) (v1.1.54)
- [x] Add BOOKED and LOST pipeline statuses (v1.1.54)
- [x] Add "Mark as Booked" workflow on dashboard (v1.1.54)

### Analytics & Reporting
- [ ] Add venue outreach timeline visualization
- [x] Add conversion funnel (discovered → qualified → pitched → replied → booked) (v1.1.58)
- [x] Add "scene health" dashboard: total venues, response rate, booking rate (v1.1.58)
- [ ] Add monthly/weekly email digest of pipeline activity
- [x] Add venue "warmth" score based on interaction recency and sentiment (v1.1.58)
- [ ] Export leads/contacts to CSV

### Additional Scrapers
- [ ] Add Facebook Events scraper for Detroit-area event discovery
- [ ] Add Eventbrite scraper for Detroit electronic music events
- [ ] Add Meetup.com scraper for Detroit DJ/music groups

### A/B Testing Formalization
- [ ] Implement A/B testing engine with experiment tracking
- [ ] Add statistical significance calculator (stop testing when variant wins)
- [ ] Add multi-media pitch sequences (mix + visuals + EPK in different combinations)

---

## 🔵 Low Priority (Future / Nice-to-Have)

- [ ] Add video analysis in venue qualification
- [ ] Expand geocoding to support full address parsing from raw text
- [ ] Add email open/click tracking via tracking pixel or link wrapper
- [ ] Add per-artist analytics for multi-artist collectives
- [ ] Add collaborative filtering (if rejected at Venue A, suggest Venue B with similar vibe)
- [ ] Add Instagram Stories scraper for real-time venue atmosphere
- [ ] Add shared dashboard login for collective members
- [ ] Add Facebook Events / Eventbrite / Meetup scrapers
