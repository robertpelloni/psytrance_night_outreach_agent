# Psytrance Night Outreach Agent

> **Automated venue scouting and outreach for underground electronic music — built for the Detroit psytrance scene.**

## What It Does

This agent autonomously discovers venues, qualifies them for psychedelic music fit, generates personalized booking pitches, and manages the entire outreach lifecycle — with a human-in-the-loop safety net.

**Reliability & Performance:**
The system has maintained **100% pipeline stability** through v1.1.63, confirming the robustness of the Multi-Artist Collective architecture and Usage Tracking integration.

### Technical Integrity
- **Pipeline Success Rate**: 100% (Detroit Baseline)
- **Master Integrity Suite**: 88/88 tests PASSED (v1.1.63)
- **Scraper Resilience**: Exponential backoff (2^n) + Dynamic Proxy Rotation
- **Hardened Error Isolation**: Per-venue isolation prevents cascading discovery failures

Detailed metrics are documented in [PERFORMANCE.md](PERFORMANCE.md).

**The Pipeline:**
```
Hunt → Enrich → Qualify → Pitch → Review (HITL) → Dispatch → Follow Up → Negotiate
```

## Quick Start

```bash
# 1. Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Configure
cp .env.template .env          # Add your OpenAI key, SMTP creds
# Edit database/config.json    # Set artist name, EPK link, cities

# 3. Run
python main.py                 # Full discovery + qualification pipeline
python src/dashboard/app.py    # HITL review dashboard at http://localhost:5000
```

## Architecture

| Layer | Tech | Purpose |
|-------|------|---------|
| **Scraping** | Playwright + Proxy/UA rotation | Google Maps, Resident Advisor, Instagram |
| **AI** | OpenAI GPT-4o (+ Vision) | Vibe scoring, pitch generation, sentiment analysis, trait extraction |
| **Data** | SQLite | Venues, contacts, leads, replies, system logs |
| **Outreach** | SMTP | Email dispatch, follow-ups, reply negotiation |
| **Dashboard** | Flask + Leaflet.js | HITL review, analytics, map, tour planning, settings |
| **DevOps** | GitHub Actions + sync_repo.py | CI/CD, branch reconciliation, AI merge conflict resolution |

## Key Capabilities

- **Multi-source discovery**: Google Maps, Resident Advisor, Instagram, AI-generated scrapers
- **Detroit-optimized search**: Neighborhood-aware queries (Corktown, Midtown, Hamtramck, etc.)
- **Vision-enriched qualification**: GPT-4o analyzes venue images for aesthetic fit
- **AI trait extraction**: Sound system, lighting, atmosphere, music policy parsed from descriptions
- **3 pitch variants**: Professional, Underground, Technical — with epsilon-greedy A/B optimization
- **Outreach prediction**: Success probability based on vibe score, city history, and trait alignment
- **Sentiment-driven negotiation**: Auto-drafts replies to venue responses
- **Geographic intelligence**: Interactive map, proximity clustering, AI tour routing
- **Artist identity**: Configurable artist name, collective, EPK/mix links baked into every pitch

## Project Structure

```
├── main.py                  # Pipeline orchestrator
├── src/
│   ├── ai_engine.py         # GPT-4o integration (vibe check, pitch, vision, sentiment)
│   ├── db_manager.py        # SQLite data layer
│   ├── config_manager.py    # Dynamic configuration (cities, genres, media, identity)
│   ├── outreach_engine.py   # Email dispatch + auto-approval
│   ├── follow_up_engine.py  # Automated follow-up cycles
│   ├── outreach_predictor.py# Success probability scoring
│   ├── sentiment_analyzer.py# Reply sentiment classification + draft orchestration
│   ├── tour_planner.py      # AI-driven tour routing + cluster pitches
│   ├── analytics.py         # Stats, approval rates, variant performance, clustering
│   ├── geocoding.py         # Nominatim + AI-fallback coordinate resolution
│   ├── mailer.py            # SMTP email dispatch
│   ├── scraper_generator.py # AI-powered scraper creation from URL
│   ├── pipeline_monitor.py  # CI/CD event logging
│   ├── reliability_monitor.py# Sync health + stale branch detection
│   ├── version_auditor.py   # Git → DB audit trail harvesting
│   ├── dashboard/           # Flask HITL dashboard
│   │   ├── app.py
│   │   └── templates/       # index, map, analytics, settings, sources, system
│   └── scrapers/
│       ├── base_scraper.py  # ProxyRotator, UserAgentRotator, ContactExtractor
│       ├── google_maps.py   # Playwright Google Maps scraper
│       ├── resident_advisor.py # RA discovery + enrichment scraper
│       └── instagram.py     # IG profile context scraper
├── database/
│   ├── schema.sql
│   └── config.json
├── tests/                   # 36 test files (Master Integrity Suite)
├── .github/workflows/       # 5 CI/CD workflows
└── sync_repo.py             # Autonomous repository synchronization protocol
```

## Configuration

All runtime settings live in `database/config.json` and are editable via the Dashboard Settings page:

| Setting | Description |
|---------|-------------|
| `cities` | Target cities for venue discovery |
| `target_genres` | Genres for qualification and pitch generation |
| `artist_name` | Your DJ/artist name — injected into all pitches |
| `collective_name` | Your collective/crew name |
| `home_city` | Primary city (used for Detroit-specific search strategies) |
| `epk_link` | Electronic Press Kit URL |
| `mix_link` | Showcase mix URL |
| `vibe_threshold` | Minimum score (1-10) to generate a pitch |
| `media_library` | Tagged library of mixes/visuals for contextual matching |
| `detroit_search_queries` | Detroit-specific Google Maps search phrases |
| `detroit_neighborhoods` | Neighborhoods for deep local search |

## Environment Variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | GPT-4o API key |
| `SMTP_SERVER` | For email | SMTP host |
| `SMTP_PORT` | For email | SMTP port (default 587) |
| `SMTP_USER` | For email | SMTP username |
| `SMTP_PASSWORD` | For email | SMTP password |
| `SENDER_EMAIL` | For email | Outbound booking email address |
| `PROXY_LIST` | Optional | Comma-separated proxy URLs |
| `DB_PATH` | Optional | Override database path (for staging/production isolation) |

## Documentation

- **[MANUAL.md](MANUAL.md)** — Full user manual
- **[DEPLOY.md](DEPLOY.md)** — Deployment and CI/CD guide
- **[ROADMAP.md](ROADMAP.md)** — Development roadmap and phase history
- **[TODO.md](TODO.md)** — Task tracker
- **[VISION.md](VISION.md)** — Project vision and design philosophy
- **[IDEAS.md](IDEAS.md)** — Future feature ideas
- **[CHANGELOG.md](CHANGELOG.md)** — Version history

## License

Private project. Not for redistribution.
