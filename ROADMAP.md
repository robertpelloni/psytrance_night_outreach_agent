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

---

## Upcoming Phases

### Phase 37: Real-World Scraper Hardening (v1.1.45)
The current scrapers work in principle but are fragile in practice. Google Maps CSS selectors change frequently, RA has aggressive Cloudflare protection, and Instagram requires login for most profiles. This phase makes discovery reliable enough for production use.

- [ ] Add retry logic with exponential backoff to all scrapers (max 3 retries per query)
- [ ] Add per-venue try/catch isolation so one bad result doesn't kill a city run
- [ ] Validate scraper output: reject venues with empty names, duplicate IDs, or missing city
- [ ] Add rate limiting between scraper calls (2-5 second delay) to avoid IP bans
- [ ] Add a dedicated Detroit venue knowledge base (`database/detroit_venues_seed.json`) with known venues to bootstrap the pipeline
- [ ] Implement Google Maps Places API as a reliable fallback when Playwright selectors break
- [ ] Add scraper health tracking: log success/failure rates per scraper per city to `system_logs`
- [ ] Add a "dry run" mode to `main.py` that reports what would be discovered without making AI calls

### Phase 38: Email Inbox Integration (v1.1.46)
Currently, venue replies must be manually pasted into the "Simulate Reply" form. This is the single biggest usability gap — in production, replies arrive in the booking inbox and must be ingested automatically.

- [ ] Implement IMAP inbox polling (`src/inbox_monitor.py`) to fetch unread emails from the booking mailbox
- [ ] Match incoming emails to leads by sender address or venue name in subject/body
- [ ] Auto-route matched emails through `SentimentAnalyzer.process_new_reply()`
- [ ] Add dashboard notification for new replies requiring attention
- [ ] Add an "Unmatched Replies" view for emails that can't be auto-matched
- [ ] Poll on configurable interval (default: every 15 minutes)
- [ ] Handle bounce emails: detect SMTP bounces and mark leads as BOUNCED

### Phase 39: Pipeline Scheduling & Cycle Management (v1.1.47)
The pipeline currently requires manual execution. For ongoing scene-building, it needs to run on a schedule with proper cycle management.

- [ ] Integrate APScheduler into the dashboard app for automated pipeline runs
- [ ] Add configurable schedule (e.g., "run discovery every Monday at 9am")
- [ ] Implement `db.reset_city_cycle(city)` to allow re-running discovery for a city
- [ ] Add a "Reset All Cycles" button on the dashboard (for starting a fresh scouting pass)
- [ ] Add pipeline run history to the database (start time, end time, cities processed, venues found, errors)
- [ ] Add a dashboard "Pipeline" tab showing run history and next scheduled run
- [ ] Add pipeline run email/Slack notification on completion

### Phase 40: Settings & Dashboard Completeness (v1.1.48)
The Settings UI doesn't expose half the config fields. The dashboard is missing key workflows.

- [ ] Add Artist Identity section to Settings UI (artist_name, collective_name, home_city)
- [ ] Add Media Library management to Settings UI (add/edit/remove tagged media)
- [ ] Add Detroit Search Queries editor to Settings UI
- [ ] Add Detroit Neighborhoods editor to Settings UI
- [ ] Add auto_approve_threshold, follow_up_days, max_follow_ups to Settings UI
- [ ] Add "PENDING_QUALIFICATION" view to dashboard (venues that scored below threshold but exist)
- [ ] Add venue detail page with full venue info, all contacts, all leads, and reply history
- [ ] Fix map default center to Detroit (42.3314, -83.0458) instead of world view
- [ ] Add "Re-qualify" button on PENDING_QUALIFICATION leads (re-run vibe check after editing venue text)

### Phase 41: Outreach Intelligence & Safety (v1.1.49)
The outreach engine needs guardrails to protect sender reputation and optimize conversion.

- [ ] Add daily outreach throttle (max N emails per day, default 10) to avoid spam flags
- [ ] Add configurable delay between dispatches (e.g., 5 minutes between emails)
- [ ] Add OpenAI token budget tracker — estimate cost per run, log to database, warn if over budget
- [ ] Add pitch subject line generation (currently hardcoded as "Proposal for Psytrance Night Residency")
- [ ] Add email open/click tracking via tracking pixel or link wrapper
- [ ] Add bounce detection and lead status update (BOUNCED status)
- [ ] Add "Do Not Contact" list — venues that asked to never be emailed again
- [ ] Add A/B testing statistical significance calculator (stop testing when one variant is clearly winning)

### Phase 42: Data Model & Persistence Improvements (v1.1.50)
The database schema has several gaps that limit real-world use.

- [ ] Add `address` column to `venues` table
- [ ] Add `phone` column to `venues` table (currently only in venue_contacts)
- [ ] Add `venue_type` column (warehouse, club, bar, art_space, diy, lounge)
- [ ] Add `capacity` column to `venues` table
- [ ] Add `neighborhood` column to `venues` table for Detroit-area filtering
- [ ] Add `source` column to `venues` (google_maps, resident_advisor, instagram, manual, ai_generated)
- [ ] Add `discovered_at` timestamp to `venues`
- [ ] Add `last_verified_at` to `venue_contacts` (track when contact info was last confirmed)
- [ ] Add database indexes on frequently queried columns (city, pipeline_status, vibe_score)
- [ ] Add `pipeline_runs` table for tracking run history
- [ ] Add migration system for safe schema upgrades without data loss

### Phase 43: Detroit Venue Seed & Community Intelligence (v1.1.51)
Bootstrap the system with known Detroit venues and community knowledge.

- [ ] Create `database/detroit_venues_seed.json` with 20-30 known Detroit-area venues (TV Lounge, Marble Bar, Spot Lite, El Club, Hasrat, New Dodge Lounge, etc.)
- [ ] Add seed import command: `python main.py --seed` to load seed data
- [ ] Add "Add Venue Manually" form to dashboard (for venues found by word-of-mouth)
- [ ] Add venue notes/annotations system (free-text notes attached to any venue)
- [ ] Add Facebook Events scraper for Detroit-area event discovery
- [ ] Add Eventbrite scraper for Detroit electronic music events
- [ ] Add Meetup.com scraper for Detroit DJ/music groups

### Phase 44: Reply Automation & Negotiation Engine (v1.1.52)
Expand the reply handling from draft-only to semi-automated negotiation.

- [ ] Add auto-response for OOO replies (queue re-attempt after OOO end date)
- [ ] Add "rate inquiry" auto-draft with configurable rate card
- [ ] Add "availability inquiry" auto-draft with available date ranges
- [ ] Add negotiation state machine (INITIAL → REPLIED → NEGOTIATING → BOOKED / LOST)
- [ ] Add BOOKED and LOST pipeline statuses
- [ ] Add "Mark as Booked" workflow on dashboard with date/confirmation fields
- [ ] Add booking tracker: venue, date, deal terms, status

### Phase 45: Reporting & Scene Analytics (v1.1.53)
Turn the data into actionable intelligence for scene-building.

- [ ] Add venue outreach timeline visualization (first contact → replies → booked)
- [ ] Add conversion funnel visualization (discovered → qualified → pitched → replied → booked)
- [ ] Add "scene health" dashboard: total venues contacted, response rate, booking rate, average time-to-first-reply
- [ ] Add monthly/weekly email digest of pipeline activity
- [ ] Add venue "warmth" score based on interaction recency and sentiment
- [ ] Export leads/contacts to CSV for use in other tools
- [ ] Add venue comparison view (side-by-side for decision making between similar venues)

### Phase 46: Multi-Artist & Collaboration (v1.1.54)
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
