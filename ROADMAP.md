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
- [ ] Add venue notes/annotations system

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
- [ ] Refine "Pending Qualification" view with bulk approval actions

---

### Phase 50: Automated Follow-up & Sentiment Engine

Expand reply parsing logic to deeply integrate sentiment and trigger automatic follow-ups.

- [ ] Implement sentiment analysis for incoming DM responses to auto-tag lead warmth
- [ ] Build automated follow-up triggers for positive DM leads (low-friction guidelines)
- [ ] Add DM lead tracking visibility to the HITL dashboard

## Backlog / Future Ideas

See [IDEAS.md](IDEAS.md) for unconstrained future feature ideas.

### Phase 4 Outreach Execution Enhancements
- [x] Integrate SMTP logic with `.env` loading and establish a dry-run test suite.
- [x] Hook IG/FB DM templates directly into the `AIEngine` pitch generator and trigger simulated DM execution.
- [x] Fix concurrent database write locks during the primary outreach dispatch cycle.

### Phase 4 Outreach Execution Enhancements
- [x] Integrate A/B testing selection and IG DM pitch generation dynamically based on data availability in the primary qualification loop.
