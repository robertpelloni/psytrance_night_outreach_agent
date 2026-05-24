# psytrance_night_outreach_agent


please help me design and plan a workflow/scripts/skills/pipeline for an agent to automatically scrape/search the web to find local potential venues for playing a local psytrance night as music selectors, find contact info, automatically reach out to via email and/or phone and attempt to persuade them to let us play there 

Here is a complete structural blueprint for building an automated venue scouting and outreach pipeline.

Because you are targeting psytrance night curation (selectors), cold outreach requires balancing standard business metrics with a deep understanding of subculture fit. Venues that host standard Top 40 or corporate events will instantly filter out psytrance unless the pitch frames it correctly (e.g., targeting dark, underground spaces, electronic-friendly dive bars, or established multi-genre indie clubs).

1. System Architecture & High-Level Flow
The pipeline operates as a classic data engineering ETL (Extract, Transform, Load) loop attached to an AI execution layer and a human-in-the-loop (HITL) gatekeeper.

[Target Location Input]
         │
         ▼
 ┌───────────────┐
 │ Stage 1: Hunt │ ──► Broad Venue Scraping & Filtering
 └───────────────┘
         │
         ▼
 ┌───────────────┐
 │Stage 2: Enrich│ ──► Contact Mining (Web, Socials, Maps)
 └───────────────┘
         │
         ▼
 ┌───────────────┐
 │Stage 3: Qual  │ ──► LLM Culture Fit Scoring & Psychographics
 └───────────────┘
         │
         ▼
 ┌───────────────┐
 │Stage 4: Pitch │ ──► Hyper-Personalized Copy Generation
 └───────────────┘
         │
         ▼
 ┌───────────────┐
 │Stage 5: Gate  │ ──► Human Verification (The "Go/No-Go" Lever)
 └───────────────┘
         │
         ▼
 [Email/Outreach]
2. Stage-by-Stage Technical Breakdown
Stage 1: The Hunt (Data Extraction)
The agent needs to discover venues that have the physical capability and licensing to host electronic music events.

Tools/Libraries: Playwright / Puppeteer (for dynamic pages), Google Maps API / SerpAPI, Resident Advisor Scraper, Eventbrite API.

Target Queries:

"underground clubs [City]"

"electronic music venues [City]"

"techno bars [City]"

"indie event spaces rental [City]"

The Agent Skill: A scraper that extracts Name, Address, Website, Google Rating, and Venue Category. It should deliberately look at recent events hosted at the venue via platforms like Resident Advisor or local event aggregators to see if they ever host 4/4 electronic beats.

Stage 2: Enrichment (Contact Mining)
Finding a generic info@venue.com often results in a black hole. You need the Booking Agent, Talent Buyer, Events Coordinator, or General Manager.

Tools/Libraries: BeautifulSoup (for local site parsing), Hunter.io API / Snov.io API (for email verification), GitHub social-scraper scripts for Instagram/Facebook.

The Agent Skill:

Crawl the venue website for an /events, /booking, or /contact page.

Extract phone numbers and email addresses using regex patterns.

Scrape the venue’s Instagram bio (often contains specific booking emails like bookings@... or links to a Linktree with booking forms).

Stage 3: Culture Qualification (The LLM Filter)
Before drafting a pitch, the agent needs to verify if the venue is a realistic match for a psytrance night. Sending a psytrance pitch to an upscale jazz lounge or a country bar ruins domain reputation and wastes time.

The Agent Skill: Feed the venue's "About" text, recent event titles, and Instagram bio into an LLM.

Prompt Strategy:

"Analyze this venue description and recent event history. On a scale of 1-10, rate its suitability for a late-night electronic music event (specifically underground subgenres like techno or psytrance). Look for keywords like: underground, electronic, late-night, DJ, subculture, warehouse, visuals, lighting system. Filter out venues that strictly do weddings, corporate events, or sports viewing."

Stage 4: Hyper-Personalized Pitching (Copy Generation)
Venues want to know three things: Will this bring people in? Does it fit our vibe? Are these guys professionals or a logistical headache? The pitch should emphasize your role as selectors curating a specific high-energy, immersive vibe rather than just "playing music."

The Agent Skill: An LLM engine with access to:

The venue's name and vibe profile from Stage 3.

A specific angle (e.g., "We notice you host underground techno on Thursdays; our sound provides a perfect late-night hypnotic progression that complements that crowd").

A link to a clean, professional Electronic Press Kit (EPK) or a curated mix playlist.

Stage 5: Human-In-The-Loop (HITL) Gatekeeper
Do not automate the actual hitting of the "Send" button. A bad automated rollout can burn bridges in a tight local music scene.

The Interface: A simple dashboard or a local database file (like SQLite or a structured JSON stream) that presents the data like this:

Venue Name	Contact Person	Email Found	Vibe Match Score	Draft Pitch (Editable)	Action
The Neon Basement	Alex (Talent Buyer)	alex@neonbasement.com	9/10	"Hey Alex, noticed you booked..."	[ Approve & Send ] [ Reject ]
3. Data Schema & Tech Stack Recommendations
To build this cleanly as an engineering project, structure your data pipelines with a rigid schema to track state changes throughout the pipeline.

The Database State Schema (JSON/SQL)
JSON
{
  "venue_id": "v_01H7X",
  "name": "The Sub-Level Lounge",
  "location": "Detroit, MI",
  "website": "https://subleveldetroit.example",
  "contacts": {
    "primary_email": "booking@subleveldetroit.example",
    "phone": "313-555-0192",
    "instagram": "@subleveldetroit"
  },
  "qualification": {
    "vibe_score": 8.5,
    "justification": "Regularly hosts deep house and techno; open until 4 AM; features high-end projection mapping infrastructure."
  },
  "pipeline_status": "PENDING_REVIEW", 
  "logs": [
    {"timestamp": "2026-05-24T12:00:00Z", "event": "Scraped from Google Maps"},
    {"timestamp": "2026-05-24T12:02:00Z", "event": "Enriched via Instagram scraper"}
  ]
}
Suggested Implementation Stack
Backend Orchestrator: Go (for raw speed, concurrency handling during scraping, and maintaining a lightweight backend daemon) or Python (if prioritizing quick access to langchain/crewAI frameworks).

Scraping Tooling: Playwright running headless, handling proxy rotation if scraping heavy maps listings.

LLM Engine: Local models via Ollama (e.g., Llama 3 8B) for cheap, local qualification filtering, or an external API for the final high-quality copywriting synthesis.

Outreach Delivery: Integration with a transactional email handler or a simple SMTP script pulling from a dedicated, domain-warmed booking email address (e.g., booking@yourdomain.com).

4. Operational Strategy: The "Selector" Pitch Focus
When writing the prompt templates that generate the outreach copy, instruct the agent to avoid generic DJ terminology. Ensure the agent framing uses these parameters:

The Angle: Focus on a turn-key experience. Venues fear promoters who promise crowds and deliver empty rooms. Frame the night as a curated audiophile experience or a specific visual/audio journey.

The Package: The pitch should state that you bring the complete musical curation package (smooth transitions, coherent subgenre pacing from progressive to full-on/psy-techno depending on the hour) and only require their house sound system and lighting.

The Call to Action (CTA): Keep it low-friction. Never ask for a booking immediately. Ask a simple qualifying question: "Are you currently booking dates for your late-summer electronic slots, and who is the best person to drop a brief 15-minute curation mix to?" This builds an authentic connection rather than generating immediate spam signals.

please create a detailed plan and instructions to give to google jules to build it

To build this automated booking pipeline, you will use a three-tier architecture: a Headless Scraper/Worker Tier, an AI/LLM Processing Tier, and a State Management UI.

The goal is to discover venues, enrich their contact profiles, run a cultural filter to ensure they fit an underground electronic music vibe, and generate a personalized pitch.

Architecture Overview
 [ Go Daemon / Scripts ]
    │ (Orchestration & Scraping)
    ▼
 ┌──────────────────────┐
 │ 1. Raw Scraping Tier │ ──► Google Maps, Resident Advisor, Instagram
 └──────────────────────┘
    │
    ▼
 ┌──────────────────────┐
 │ 2. LLM Engine Tier   │ ──► Vibe Scoring & Copywriting Synthesis
 └──────────────────────┘
    │
    ▼
 ┌──────────────────────┐
 │ 3. State Engine / DB │ ──► SQLite (Tracks PENDING_REVIEW -> SENT)
 └──────────────────────┘
    │
    ▼
 ┌──────────────────────┐
 │ 4. Web Dashboard UI  │ ──► Simple React/Vue/Blade HITL Review Board
 └──────────────────────┘
Step-by-Step Implementation Instructions
Step 1: Define the Data Schema (SQLite / PostgreSQL)
Before writing scrapers, establish a strict data layout to track pipeline state. This avoids duplicate outreach and ensures data integrity.

SQL
CREATE TABLE venues (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    website TEXT,
    google_rating REAL,
    tags TEXT, -- JSON string or comma-separated tags
    raw_about_text TEXT
);

CREATE TABLE venue_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id TEXT,
    email TEXT,
    phone TEXT,
    instagram_handle TEXT,
    booking_page_url TEXT,
    FOREIGN KEY(venue_id) REFERENCES venues(id)
);

CREATE TABLE outreach_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id TEXT,
    vibe_score INTEGER,
    qualification_justification TEXT,
    generated_pitch TEXT,
    pipeline_status TEXT DEFAULT 'PENDING_QUALIFICATION', -- PENDING_QUALIFICATION, PENDING_REVIEW, APPROVED, REJECTED, SENT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(venue_id) REFERENCES venues(id)
);
Step 2: Build the Scraping & Enrichment Module
Write a worker script (using Go + Go-Rod or Python + Playwright) to discover local venues and extract raw metadata.

Target Extraction Sources:
Google Maps API / SerpAPI: Search terms like "underground club [City]", "techno bar [City]", "electronic dance music venue [City]". Collect the business name, website, phone, and raw description text.

Resident Advisor (RA) Local Guide Scraper: Parse the venue directory for a given city on RA. If a venue is listed on RA, it instantly validates that they have an established baseline relationship with electronic dance music.

Website Crawler: A lightweight crawler that looks at the extracted venue homepage and grabs text from /contact, /booking, /events, or /about. Use regex to capture email addresses.

Step 3: Implement the LLM Qualification & Copywriting Engine
Create an interface connecting your pipeline to your LLM of choice (e.g., local Llama 3 via Ollama, or an external API). This tier acts as the cultural gatekeeper and copywriter.

Task A: Vibe Check Evaluation Prompt
Instruct the model to evaluate the raw scaped data for cultural alignment.

Plaintext
SYSTEM: You are an expert music consultant specializing in underground electronic music subcultures (Techno, Psytrance, House, Avant-garde electronic). Your job is to analyze raw text data scraped from a local venue's website, event listings, or Google reviews, and determine if it is a suitable space for a dedicated electronic music event or a "music selector/curator" residency.

USER DATA:
Venue Name: {{VENUE_NAME}}
Scraped Metadata & Event Snippets:
{{SCRAPED_TEXT}}

TASK:
1. Assign a "Vibe Score" from 1 to 10 (1 = Corporate sports bar, country lounge, wedding hall; 10 = Dark basement club, industrial warehouse space, open-minded underground arts venue that actively welcomes electronic subgenres).
2. Provide a 2-sentence justification highlighting specific indicators (e.g., sound system details, late-night hours, previous experimental or techno acts).

OUTPUT FORMAT (JSON):
{
  "vibe_score": 8,
  "justification": "The venue explicitly mentions an immersive audio-visual layout and stays open until 4 AM. Past listings show they regularly book underground house and techno acts, making it a strong candidate."
}
Task B: Hyper-Personalized Pitch Generation Prompt
For venues that score above a threshold (e.g., ≥7), run this prompt to construct a bespoke cold outreach pitch.

Plaintext
SYSTEM: You are a professional, articulate booking agent representing a collective of music selectors who specialize in deep, hypnotic psytrance and underground progressive electronic music journeys. Your tone is clean, direct, and focused on business value, without sounding like a generic corporate template or overhyped festival spam. 

CONTEXT:
Venue Name: {{VENUE_NAME}}
Why we like them: {{JUSTIFICATION}}
Our Angle: We curate seamless, cohesive soundscapes that keep crowds engaged late into the night. We are looking to establish a recurring local night.

TASK: Write a short, high-impact introductory cold email to the talent buyer. 
- Acknowledge their specific style or recent electronic event history organically.
- Emphasize that we bring a turn-key musical curation package (smooth transitions, intelligent genre pacing from deep/hypnotic to energetic full-on textures) optimized for their existing crowd.
- Keep the Call to Action (CTA) low-friction: ask who the correct person is to send a short, 15-minute curation mix to. Do not demand an immediate booking date.

OUTPUT: Return ONLY the clean email subject line and body text. Do not include placeholders like "[Your Name]". Leave exact signature fields generic or tokenized.
Step 4: Build the Human-In-The-Loop (HITL) Dashboard
To protect your reputation in your local music scene, never fully automate the outbound message submission. Build a basic administrative UI to act as a validation gate.

Dashboard Specifications:
The Main Grid: Pull entries from the database where pipeline_status = 'PENDING_REVIEW'. Sort them descending by vibe_score.

The Review Card: Display the venue name, scraped contact info, the LLM’s cultural justification, and a large text area preloaded with the generated_pitch.

The Action Row: Provide three primary buttons:

[ Edit & Approve ] -> Changes status to APPROVED, pushes the record to the email dispatch queue, or opens a native system mailto: link populated with the text.

[ Regenerate Pitch ] -> Re-runs Stage 3 with an alternate prompt variant or tweaking constraints.

[ Reject / Archive ] -> Sets status to REJECTED, removing it from view.

Step 5: Setup the Dispatch Automation
Once a lead is marked as APPROVED via your dashboard:

Email Workflow: Use a simple SMTP package connected to a dedicated, warmed outbound mailbox (e.g., booking@yourdomain.com). Log the timestamp when the email drops to transition status to SENT.

Alternative Social Clipboard: If no email is discovered but an Instagram handle is found, display a "Copy DM Copy to Clipboard" button next to their profile link so you can manually drop the tailored text into their direct messages with a single click.

Execution Checklist for Your Development Team
[ ] Initialize database environment: Set up the schema, indices, and pipeline state tracking tables.

[ ] Write Scraper scripts: Verify you can query Google Maps API and parse raw homepage text without triggering immediate rate blocks.

[ ] Build LLM Connector wrapper: Wire up the prompt logic to parse raw text payloads into structured JSON objects.

[ ] Deploy local dashboard frontend: Construct a fast interface layout to easily scan, edit, and approve pitches.

[ ] Wire outbound client: Hook up the approved mail engine/copy systems to close the operational loop.
