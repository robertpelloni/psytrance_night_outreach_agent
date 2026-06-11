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
The current scrapers work in principle but are fragile in practice. This phase makes discovery reliable enough for production use.
- [x] Add retry logic with exponential backoff to `GoogleMapsPlaywrightScraper`
- [x] Implement per-venue try/catch isolation in `main.py`
- [x] Validate scraper output (reject empty names/missing cities)
- [x] Add rate limiting between scraper calls
- [x] Implement pipeline "dry run" mode

### Phase 38: Dynamic Proxy Rotation & Multi-Scraper Hardening (v1.1.46-v1.1.47)
Further strengthen bot mitigation by tracking proxy health and rotating based on performance.
- [x] Implement health tracking in `ProxyRotator` (success/fail counts)
- [x] Add exponential backoff blacklisting for failing proxies
- [x] Integrate feedback loop from scrapers (success/failure reporting)
- [x] Apply production hardening (retries + isolation) to RA and Instagram scrapers
- [x] Optimized discovery loop to separate query-based vs. city-based scrapers (v1.1.48)
- [x] Verified 100% stability across Master Integrity Suite (v1.1.46 Report)
- [x] Conducted v1.1.46 Performance Review (See PERFORMANCE.md)

### Phase 39: Email Inbox Integration (v1.1.49)
Currently, venue replies must be manually pasted into the "Simulate Reply" form. This is the single biggest usability gap — in production, replies arrive in the booking inbox and must be ingested automatically.

- [x] Implement IMAP inbox polling (`src/inbox_monitor.py`) to fetch unread emails from the booking mailbox
- [x] Match incoming emails to leads by sender address or venue name in subject/body
- [x] Auto-route matched emails through `SentimentAnalyzer.process_new_reply()`
- [x] Add "Fetch New Replies" button to the HITL Dashboard (v1.1.49)
- [ ] Add dashboard notification for new replies requiring attention
- [ ] Add an "Unmatched Replies" view for emails that can't be auto-matched
- [x] Poll on configurable interval (integrated into main pipeline cycle)
- [ ] Handle bounce emails: detect SMTP bounces and mark leads as BOUNCED

### Phase 40: Pipeline Scheduling & Cycle Management (v1.1.50)
The pipeline currently requires manual execution. For ongoing scene-building, it needs to run on a schedule with proper cycle management.

- [x] Integrate APScheduler into the dashboard app for automated pipeline runs
- [x] Add configurable schedule (default: weekly)
- [x] Implement `db.reset_city_cycle(city)` to allow re-running discovery for a city
- [x] Add a "Reset All Cycles" button on the dashboard (System tab)
- [x] Add pipeline run history to the database (start time, end time, cities processed, venues found, errors)
- [x] Add a dashboard visualization showing run history and status
- [ ] Add pipeline run email/Slack notification on completion

### Phase 41: Settings & Dashboard Completeness (v1.1.51)
The Settings UI doesn't expose half the config fields. The dashboard is missing key workflows.

- [x] Add Artist Identity section to Settings UI (artist_name, collective_name, home_city)
- [x] Add Media Library management to Settings UI (add/edit/remove tagged media)
- [x] Add Detroit Search Queries editor to Settings UI
- [x] Add Detroit Neighborhoods editor to Settings UI
- [x] Add auto_approve_threshold, follow_up_days, max_follow_ups to Settings UI
- [x] Add "PENDING_QUALIFICATION" view to dashboard (venues that scored below threshold but exist)
- [x] Add venue detail page with full venue info, all contacts, all leads, and reply history
- [x] Fix map default center to Detroit (42.3314, -83.0458) instead of world view
- [x] Add "Re-qualify" button on PENDING_QUALIFICATION leads (re-run vibe check after editing venue text)

### Phase 42: Outreach Intelligence & Safety (v1.1.51)
The outreach engine needs guardrails to protect sender reputation and optimize conversion.

- [x] Add daily outreach throttle (max N emails per day, default 10) to avoid spam flags
- [x] Add configurable delay between dispatches (e.g., 5 minutes between emails)
- [ ] Add OpenAI token budget tracker — estimate cost per run, log to database, warn if over budget
- [ ] Add pitch subject line generation (currently hardcoded as "Proposal for Psytrance Night Residency")
- [ ] Add email open/click tracking via tracking pixel or link wrapper
- [ ] Add bounce detection and lead status update (BOUNCED status)
- [ ] Add "Do Not Contact" list — venues that asked to never be emailed again
- [ ] Add A/B testing statistical significance calculator (stop testing when one variant is clearly winning)

### Phase 43: Data Model & Persistence Improvements (v1.1.52)
The database schema has several gaps that limit real-world use.

- [x] Add `address` column to `venues` table
- [x] Add `phone` column to `venues` table
- [x] Add `venue_type` column (warehouse, club, bar, art_space, diy, lounge)
- [x] Add `capacity` column to `venues` table
- [x] Add `neighborhood` column to `venues` table for Detroit-area filtering
- [x] Add `source` column to `venues` (google_maps, resident_advisor, instagram, manual, ai_generated)
- [x] Add `discovered_at` timestamp to `venues`
- [ ] Add `last_verified_at` to `venue_contacts` (track when contact info was last confirmed)
- [ ] Add database indexes on frequently queried columns (city, pipeline_status, vibe_score)
- [x] Add `pipeline_runs` table for tracking run history
- [x] Add migration system for safe schema upgrades without data loss

### Phase 44: Detroit Venue Seed & Community Intelligence (v1.1.51)
Bootstrap the system with known Detroit venues and community knowledge.

- [x] Create `database/detroit_venues_seed.json` with 20-30 known Detroit-area venues (TV Lounge, Marble Bar, Spot Lite, El Club, Hasrat, New Dodge Lounge, etc.)
- [x] Add seed import command: `python main.py --seed` to load seed data
- [ ] Add "Add Venue Manually" form to dashboard (for venues found by word-of-mouth)
- [ ] Add venue notes/annotations system (free-text notes attached to any venue)
- [ ] Add Facebook Events scraper for Detroit-area event discovery
- [ ] Add Eventbrite scraper for Detroit electronic music events
- [ ] Add Meetup.com scraper for Detroit DJ/music groups

### Phase 45: Reply Automation & Negotiation Engine (v1.1.54)
Expand the reply handling from draft-only to semi-automated negotiation.
- [x] Add auto-response for OOO replies (v1.1.54)
- [x] Add "rate inquiry" auto-draft with configurable rate card (v1.1.54)
- [x] Add "availability inquiry" auto-draft with available date ranges (v1.1.54)
- [x] Add negotiation state machine (INITIAL → REPLIED → NEGOTIATING → BOOKED / LOST) (v1.1.54)
- [x] Add BOOKED and LOST pipeline statuses (v1.1.54)
- [x] Add "Mark as Booked" workflow on dashboard (v1.1.54)
- [x] Add booking tracker: venue, date, deal terms, status (v1.1.54)

### Phase 46: Reporting & Scene Analytics (v1.1.58)
Turn the data into actionable intelligence for scene-building.
- [x] Add conversion funnel visualization (discovered → qualified → pitched → replied → booked)
- [x] Add "scene health" dashboard: total venues contacted, response rate, booking rate
- [x] Add venue "warmth" score based on interaction recency and sentiment
- [x] Implemented Analytics Engine backend with automated health KPIs
- [ ] Add venue outreach timeline visualization (first contact → replies → booked)
- [ ] Add monthly/weekly email digest of pipeline activity
- [ ] Export leads/contacts to CSV for use in other tools
- [ ] Add venue comparison view (side-by-side for decision making between similar venues)

---

## Upcoming Phases

### Phase 47: Multi-Artist & Collaboration (v1.1.58)
Enable the system to support multiple artists or a collective.

- [ ] Add artist profiles table (name, bio, genres, links, rate card)
- [ ] Allow pitches to reference specific artists from the collective
- [ ] Add "billed artist" field to leads (which artist the pitch is for)
- [ ] Add collaborative filtering: if Artist A gets rejected at a venue, suggest Artist B with a different style
- [ ] Add shared dashboard login for collective members
- [ ] Add per-artist analytics (response rates, booking rates by artist)

---

## Backlog / Future Ideas

See [IDEAS.md](IDEAS.md) for unconstrained future feature ideas.
