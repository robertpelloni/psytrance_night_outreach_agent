# USER MANUAL: Psytrance Night Outreach Agent

Welcome to the **Psytrance Night Outreach Agent** — a Detroit-first automated venue scouting and outreach system for underground electronic music curators.

---

## 1. Overview

The agent follows a multi-stage pipeline:

1. **Hunt**: Scrapes Google Maps, Resident Advisor, and Instagram for venues in target cities using neighborhood-aware search queries.
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

### Dashboard Tabs

| Tab | Purpose |
|-----|---------|
| **Pending** | Review qualified leads sorted by vibe score. Edit pitches, approve & send, or reject. |
| **History** | View all SENT/REJECTED leads with reply threads, sentiment tags, and AI-drafted responses. |
| **Map** | Interactive Leaflet.js map with venue markers, vibe-score coloring, status/vibe filters, hotspot clusters, and AI tour planning. |
| **Analytics** | Total venues, approval rate, status breakdown, city distribution, A/B variant performance. |
| **Sources** | View active scrapers and generate new ones from a URL via AI. |
| **Settings** | Configure cities, genres, EPK/mix links, and vibe threshold. |
| **System** | Git status, branch health, sync reliability, version audit trail, manual sync trigger. |

### Key Workflows

- **Approve & Send**: Edit the AI-generated pitch, click "Approve & Send Email" → dispatches via SMTP → status changes to SENT.
- **Regenerate Pitch**: Click "Regenerate AI Pitch" for a fresh take on the same venue.
- **Instagram DM**: If a venue has an IG handle but no email, click "Copy Pitch for DM" to clipboard the pitch text.
- **Reply Negotiation**: When a venue replies, the AI analyzes sentiment and drafts a response. You can edit the draft and send it from the History view.
- **Tour Planning**: On the Map tab, click "Show Hotspots" to see venue clusters, then click a cluster to generate an AI tour itinerary and unified cluster pitch.

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
| **Vibe Threshold** | Minimum score (1-10) to generate a pitch. Default: 6. |
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
```
