# USER MANUAL: Psytrance Night Outreach Agent

Welcome to the **Psytrance Night Outreach Agent** — a Detroit-first automated venue scouting and outreach system for underground electronic music curators.

---

## 1. Overview

The agent follows a multi-stage pipeline:

1. **Hunt**: Scrapes Google Maps, Resident Advisor, and Instagram for venues in target cities using neighborhood-aware search queries. As of **v1.1.63**, discovery is backed by a 100% stable pipeline with exponential backoff and dynamic proxy rotation, now supporting multi-artist collective scouting.
2. **Enrich**: Extracts contact information (emails, social handles) from venue websites and social profiles.
3. **Qualify**: Uses GPT-4o (text + vision) to score the "vibe" of the venue based on its description, images, and Detroit scene context.
4. **Pitch**: Generates a hyper-personalized booking proposal using one of three tone variants (Professional, Underground, Technical).
5. **Review (HITL)**: Provides a web dashboard for you to review, edit, and approve the outreach before it is sent.
6. **Dispatch**: Sends approved pitches via SMTP email.
7. **Follow Up**: Automatically nudges non-responsive leads on a configurable schedule.
8. **Negotiate**: Analyzes venue replies with AI sentiment detection and drafts professional responses.

---

## 2. Getting Started

### Prerequisites
- Python 3.9+
- Playwright
- OpenAI API Key
- SMTP Credentials (for automated emailing)

### Installation

1. **Clone the Repository**:
```bash
git clone https://github.com/robertpelloni/psytrance_night_outreach_agent
cd psytrance_night_outreach_agent
```

2. **Setup Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Configure Environment**: Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key

# SMTP Settings (required for email dispatch)
SMTP_SERVER=smtp.yourmail.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
SENDER_EMAIL=booking@yourdomain.com

# Proxy Settings (optional — for bypassing anti-bot blocks)
# Comma-separated: http://user:pass@host:port
PROXY_LIST=http://proxy1.com:8080,http://proxy2.com:8080
```

5. **Configure Your Identity**: Edit `database/config.json` and set:
```json
{
  "artist_name": "Your DJ Name",
  "collective_name": "Your Collective",
  "epk_link": "https://your-epk.com",
  "mix_link": "https://soundcloud.com/your-mix"
}
```

These fields are automatically injected into every AI-generated pitch.

---

## 3. Running the Pipeline

```bash
python main.py
```

This script will:
- Iterate through configured cities (Detroit and Midwest circuit by default).
- For Detroit-area cities, use neighborhood-aware search queries (Corktown, Midtown, Hamtramck, etc.).
- For each city, run genre-specific discovery across all configured genres (psytrance, forest psy, dark prog, etc.).
- Enrich venues with contact info and social context.
- Perform AI vibe checks with Detroit scene knowledge baked into the prompts.
- Extract venue traits (sound system, lighting, atmosphere, music policy).
- Geocode venues for the interactive map.
- Generate personalized pitches with A/B variant selection.
- Calculate success probability for each lead.
- Run the outreach and follow-up cycles.

### Pipeline Output

For each venue discovered, you'll see:
```
[Venue Name] Vibe: 8/10 | Status: PENDING_REVIEW | Genre: psytrance
```

---

## 4. Using the Dashboard (Human-In-The-Loop)

Once the pipeline has run, manage your leads through the web dashboard.

### Start the Dashboard
```bash
python src/dashboard/app.py
```
Access at: **http://localhost:5000**

### Dashboard Tabs (Unified Command Center)

The dashboard consolidates all subsystems into a single-page interface with prominent priority tabs:

| Tab | Purpose |
|-----|---------|
| **Pipeline Queues** | Review pending qualified leads, history of dispatched pitches, booked gigs, Instagram/Facebook DM queues, and scheduled follow-ups. Supports multi-selection for bulk operations and venue comparison. |
| **Circuit Map & Tour Routing** | Interactive Leaflet.js map showing Detroit and Midwest hubs (with Toronto), vibe scores, proximity clusters, and automated tour routing with cross-border logistics. |
| **Analytics & A/B Engine** | Funnel conversion statistics, scene health KPIs, warmth distribution, Chi-Square A/B variant significance testing, and periodic activity digest previews. |
| **Settings & Artist Management** | Configure target cities, genres, vibe threshold (with float precision, e.g. 6.5), collective artist profiles, media libraries, Detroit neighborhood search queries, and dispatch throttles. |
| **System & Scraper Sources** | Live health monitors, git synchronization logs, token usage tracking, and scraper generator from URL. |

### Key Workflows

- **Approve & Send**: Edit the AI-generated pitch, click "Approve & Send Email" → dispatches via SMTP → status changes to SENT.
- **Bulk Lead Operations**: Use checkboxes to select multiple pending leads and click **"Batch Approve"**, **"Batch Reject"**, or **"Batch Re-Score"**. Background workers process AI pitches asynchronously without blocking the UI.
- **Side-by-Side Venue Matrix Comparison**: Check 2 or more leads in the pipeline table and click **"Compare Selected"** to launch an interactive comparison modal evaluating vibe scores, success probabilities, sound systems, capacities, venue types, and extracted traits.
- **Regenerate Pitch**: Click "Regenerate AI Pitch" for a fresh take on the same venue.
- **Instagram DM**: If a venue has an IG handle but no email, click "Copy Pitch for DM" to clipboard the pitch text.
- **Reply Negotiation**: When a venue replies, the AI analyzes sentiment and drafts a response. You can edit the draft and send it from the History view.
- **Tour Planning & Midwest-Toronto Circuit**: Under Circuit Map, view optimized touring itineraries that anchor in Detroit and link Midwest hubs (Ferndale, Ann Arbor, Grand Rapids, Chicago, Cleveland, Columbus) and Toronto with cross-border guidance (Ambassador Bridge / Detroit-Windsor Tunnel crossings, ATA Carnet gear declarations, and USD/CAD currency guidance).
- **Venue Notes & Scene Intelligence**: On any venue detail page, record private curator notes and intelligence regarding sound engineer preferences, sound specs, and door policies. These notes are automatically injected into AI prompts when generating or regenerating residency pitches.
- **Activity Digests**: In the Analytics tab, click **"Email Pipeline Digest"** to preview and dispatch rolling metrics across 24h, 7d, or 30d periods.

---

## 5. Project Settings & Branding

Configure via the Dashboard **Settings** page or by editing `database/config.json` directly:

| Setting | What It Does |
|---------|-------------|
| **Target Cities** | Cities the agent scouts. Default: Detroit + Midwest circuit. |
| **Target Genres** | Genres for qualification and search. First genre is the "active" genre. |
| **Artist Name** | Your DJ/artist name — injected into every pitch. |
| **Collective Name** | Your crew/collective name — injected into every pitch. |
| **Home City** | Primary city (triggers neighborhood-specific search strategies). |
| **EPK Link** | Electronic Press Kit URL — linked in every pitch. |
| **Mix Link** | Showcase mix URL — linked in every pitch. |
| **Vibe Threshold** | Minimum score (1-10) to generate a pitch. Default: 6.5 (supports float precision). Calibrated for underground acoustics and corridor aesthetics. |
| **Auto-Approve Threshold** | Vibe score for automatic approval without human review. Default: 9. |
| **Follow-Up Days** | Days to wait before sending a follow-up. Default: 7. |
| **Max Follow-Ups** | Maximum follow-up emails per lead. Default: 2. |
| **Media Library** | Tagged collection of mixes/visuals — AI picks the best match per venue. |
| **Detroit Search Queries** | Custom Google Maps search phrases for the Detroit area. |
| **Detroit Neighborhoods** | Neighborhoods for deep local search coverage. |

---

## 6. Advanced Configuration

### Adding Target Cities
Edit `database/config.json`:
```json
"cities": ["Detroit", "Hamtramck", "Ferndale", "Chicago"]
```

### Adjusting the Vibe Filter
In the Settings UI or `config.json`:
```json
"vibe_threshold": 6
```
Lower = more venues pitched (wider net). Higher = more selective.

### Pitch Variants
The agent uses three pitch tones with epsilon-greedy A/B optimization:
- **Professional**: Business-oriented, value-driven, emphasizes audience and programming fit.
- **Underground**: Authentic, scene-focused, references Detroit underground legacy.
- **Technical**: Gear-talk, sound quality focus, speaks to production managers.

The system randomly explores (20%) or exploits the best-converting variant (80%).

---

## 7. Troubleshooting

| Issue | Solution |
|-------|----------|
| **Scraper returns empty results** | RA has aggressive Cloudflare protection. Try a different IP, update User-Agent, or add proxies. Google Maps selectors change frequently — check `src/scrapers/google_maps.py`. |
| **Database Locked** | Ensure only one process is writing to `database/outreach.db` at a time. |
| **AI Not Configured** | If `OPENAI_API_KEY` is missing, the agent assigns a default vibe score of 5 and a placeholder pitch. |
| **City already processed** | Once a city completes, it's skipped on the next run. Reset via the dashboard System tab or call `db.reset_city_cycle("Detroit")`. |
| **High AI costs** | Each full pipeline run makes many GPT-4o calls (vibe check + traits + pitch per venue). Monitor usage in your OpenAI dashboard. A dry-run mode is planned. |

---

## 8. Live Pilot & Environment Validation

The system has been verified for **100% pipeline stability** (v1.1.63 baseline). For detailed metrics on scraper resilience and error recovery, refer to the [Technical Performance Report](PERFORMANCE.md).

```bash
# Test connectivity to OpenAI, SMTP, and proxies
python tests/test_live_connectivity.py

# Full production-safe pilot run (single city)
./pilot_run.sh
```

---

## 9. Extending the Agent

The system is modular:

1. **Add a new scraper**: Create `src/scrapers/your_source.py`, inherit from `BaseScraper`, implement `search_venues(city, query=None)`. It will be auto-discovered by the pipeline.
2. **Generate a scraper via AI**: Use the Dashboard Sources tab — provide a URL and name, and GPT-4o will write the scraper code for you.
3. **Add new pitch variants**: Add to the `variant_prompts` dict in `src/ai_engine.py`.

---

## 10. Architecture Diagram

```
[Config + .env]
       │
       ▼
  ┌─────────┐    ┌──────────────┐    ┌──────────┐
  │ Scrapers │───▶│ Contact      │───▶│ AIEngine │
  │ (GM, RA, │    │ Extractor    │    │ (GPT-4o) │
  │  IG, AI) │    │ + IG Context │    │ + Vision │
  └─────────┘    └──────────────┘    └──────────┘
       │                  │                 │
       ▼                  ▼                 ▼
  ┌──────────────────────────────────────────────┐
  │            DatabaseManager (SQLite)           │
  │  venues · contacts · leads · replies · logs  │
  └──────────────────────┬───────────────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌──────────┐ ┌────────┐ ┌───────────┐
        │ Outreach │ │ Follow │ │ Sentiment │
        │ Engine   │ │  Up    │ │ Analyzer  │
        └──────────┘ └────────┘ └───────────┘
              │          │          │
              ▼          ▼          ▼
        ┌──────────────────────────────────┐
        │     HITL Dashboard (Flask)       │
        │  Review · Map · Analytics · Tour │
        └──────────────────────────────────┘
                         ▲
                         │
        ┌──────────────────────────────────┐
        │   Desktop System Tray / Daemon   │
        │      (src/dashboard/tray.py)     │
        └──────────────────────────────────┘
```

## Desktop Companion & System Tray

Launch the companion via `./tray.sh`:
- In desktop environments, provides an icon in the system tray to Open Dashboard, Trigger Pipeline, Fetch Replies, Run Repository Sync, and Gracefully Quit application servers.
- In headless/terminal environments, automatically falls back to an interactive CLI or background daemon monitor.
```bash
./tray.sh               # Auto-detects desktop or CLI
./tray.sh --check-status # Queries server status
./tray.sh --cmd status  # Executes one-off command
./tray.sh --shutdown-server # Gracefully stops Flask server and daemon
```

## Pipeline Activity Email Digests

Generate and dispatch periodic email digests of outreach activity:
- Available directly from the Analytics tab on the Unified Dashboard via the **"Email Pipeline Digest"** button.
- Select from 24 Hours (Daily), 7 Days (Weekly), or 30 Days (Monthly) summary windows.
- Preview the formatted HTML digest in the embedded viewer and specify an optional recipient email override.
- Or trigger programmatic dispatch via Python:
```python
from src.digest_generator import DigestGenerator
generator = DigestGenerator()
result = generator.dispatch_digest(recipient_email="booking@psycollective.org", days=7)
```

## Geographic Clustering & Transit Corridor Optimization

Analyze touring density and transit times in the **Geographic Map & Circuit Optimizer** tab:
- **DBSCAN Clustering**: Identifies regional venue density groups within configurable distance thresholds (`eps` in kilometers) and minimum venue counts.
- **Dynamic Cluster Span**: Calculates exact bounding-box radial spans (`cluster_radius_km`) and estimated highway transit drive times (`est_intercity_drive_hrs` at 80 km/h) for routing logistics.
- **Corridor Filter Badges**: Click any cluster corridor card to instantly filter the venues table and map view to that regional touring market.

## Collaborative Filtering & Sibling Venue Recommendations

When a venue rejects an outreach inquiry, is unavailable on a key tour date, or you want to expand circuit coverage:
- **Lead Queue Action**: Click **"Alternate Venues"** on any pipeline card to launch the algorithmic recommendation modal.
- **Affinity Scoring**: Calculates composite compatibility based on shared acoustic equipment (Funktion-One, Void, Danley), subgenre tags, capacity, and geographical proximity (with Haversine distance decay).
- **Venue Dossier Integration**: The venue detail view automatically displays live sibling alternatives with one-click navigation to their respective dossiers.
- **API Access**: Query programmatic recommendations directly via `GET /recommend_venues/<venue_id>?limit=5&min_score=0.2`.

## Meetup Community & Event Scraper

Discover underground electronic music gatherings and community-driven event spaces from Meetup:
- **Dynamic Query Discovery**: Scrapes public Meetup event search queries for targeted cities and musical genres.
- **Schema & Fallback Extraction**: Extracts venue names, physical addresses, and community event descriptions using schema.org `MusicEvent` JSON-LD structures and HTML card fallbacks.
- **Status Monitoring**: Operational alongside other scrapers under the **Scraper Sources** tab in the Unified Command Center (`meetup.py`).

## Eventbrite Nightlife Discovery Scraper

Scout electronic music and underground dance events from Eventbrite:
- **Dynamic Query Scraping**: Integrated into the automated scouting loop alongside Google Maps and Resident Advisor.
- **Structured Schema & Fallback**: Extracts venue names, physical addresses, and event contexts via schema.org JSON-LD scripts and HTML event card components.
- **Status Monitoring**: Monitored in real-time under the **Scraper Sources** tab in the Unified Command Center (`eventbrite.py`).

## Email Engagement & Open/Click Tracking

Track outreach engagement empirically to assess venue interest:
- **1x1 Pixel Open Tracking**: Injects an invisible GIF (`/track/open/<lead_id>.gif`) into multipart HTML emails that registers an `OPEN` event upon preview.
- **Link Click Redirection**: Replaces promotional links (Soundcloud mixes, EPK documents) with tracked redirects (`/track/click/<lead_id>?url=...`) recording `CLICK` events and destination URLs.
- **KPI Monitoring**: Real-time open rate (%) and click-through rate (%) aggregated globally under the **Analytics & A/B Testing** tab.
- **Lead Dossier Timeline**: Each venue's detail page maintains an audit history of email opens, link clicks, timestamps, and client user-agents.

## High-Precision Address Geocoding & Reverse Parsing

Ensure accurate geographic circuit routing and venue cluster mapping:
- **Progressive Fallback**: Multi-stage geocoding evaluates specific queries (`Venue + Street Address + City` -> `Street Address + City` -> `Venue + City`) before falling back to AI coordinate approximation.
- **Reverse Address Details**: Automatically extracts street addresses, postal codes, and urban neighborhood/suburb classifications directly from raw Nominatim payloads.
- **Geocode Missing Action**: Click **"📍 Geocode Missing"** on the Geographic Map tab to batch-resolve coordinates for unlocated venues asynchronously in the background.
- **Precision Indicators**: Displays GPS Located vs. Unlocated status badges on venue dossiers with an on-demand "Geocode" trigger.
