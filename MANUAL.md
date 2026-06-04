# USER MANUAL: Psytrance Night Outreach Agent

Welcome to the **Psytrance Night Outreach Agent** manual. This tool is designed for music selectors and event curators to automate the discovery and outreach process for underground electronic music venues.

---

## 1. Overview
The agent follows a five-stage pipeline:
1.  **Hunt**: Scrapes Google Maps and Resident Advisor for venues in target cities.
2.  **Enrich**: Extracts contact information (emails, social handles) from venue websites.
3.  **Qualify**: Uses AI (OpenAI) to score the "vibe" of the venue based on its description and history.
4.  **Pitch**: Generates a hyper-personalized booking proposal for high-scoring venues.
5.  **Review (HITL)**: Provides a web dashboard for you to review, edit, and approve the outreach before it is sent.

---

## 2. Getting Started

### Prerequisites
- Python 3.9+
- Playwright
- OpenAI API Key
- SMTP Credentials (for automated emailing)

### Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/robertpelloni/psytrance_night_outreach_agent
    cd psytrance_night_outreach_agent
    ```
2.  **Setup Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
4.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_openai_api_key

    # SMTP Settings (Optional for dispatch)
    SMTP_SERVER=smtp.yourmail.com
    SMTP_PORT=587
    SMTP_USER=your_email@example.com
    SMTP_PASSWORD=your_password

    # Proxy Settings (Optional for bypassing blocks)
    # Comma-separated list of proxies: http://user:pass@host:port
    PROXY_LIST=http://proxy1.com:8080,http://proxy2.com:8080
    SENDER_EMAIL=booking@yourdomain.com
    ```

---

## 3. Running the Pipeline

To start the automated discovery process, run:
```bash
python main.py
```
This script will:
- Iterate through configured cities.
- Search for "underground techno clubs" on Google Maps and RA.
- Perform an AI vibe check.
- Store results in `database/outreach.db`.

---

## 4. Using the Dashboard (Human-In-The-Loop)

Once the pipeline has run, you can manage your leads through the web dashboard.

### Start the Dashboard
```bash
python src/dashboard/app.py
```

### Automated Development Synchronization
The agent supports automated repository synchronization for local development. By running `./install_hooks.sh`, you install a Git `post-commit` hook that automatically triggers the `sync_repo.py` protocol after every commit. This ensures that your local work is continuously merged and reconciled with the remote repository.
Access it at: `http://localhost:5000`

### Dashboard Features
- **Lead Review**: See all venues that passed the AI vibe check (Score ≥ 7).
- **Vibe Score & Justification**: Understand why the AI thought the venue was a good fit.
- **Pitch Editor**: Edit the AI-generated pitch directly in the text area.
- **Regenerate AI Pitch**: Click "Regenerate" to have the AI try a different angle for that specific venue.
- **Approve & Send**: Marks the lead as approved and attempts to send the email via SMTP.
- **Reject**: Archives the lead so it doesn't appear in the pending list.
- **Instagram DM Helper**: If a venue has an Instagram handle but no email, use the "Copy Pitch for DM" button to manually outreach via social media.
- **System Control**: Use the "System" tab to monitor repository versioning and manually trigger the repository synchronization protocol (merges/conflict resolution) directly from the dashboard.

### Outreach Analytics
Access the **Analytics** tab to view your performance:
- **Total Venues**: Number of venues discovered across all cities.
- **Approval Rate**: Percentage of qualified leads that you have approved.
- **Status Breakdown**: Current state of all venues in the pipeline.
- **City Distribution**: Geographic distribution of your scouting efforts.

---

## 5. Project Settings & Branding

Use the **Settings** page to personalize the agent for your project:
- **Target Cities**: Manage which cities the agent scouts for venues.
- **Target Genres**: Define the music genres to refine scraper searches and AI qualification.
- **EPK & Mix Links**: Add your Electronic Press Kit and SoundCloud links. These are automatically integrated into every AI-generated pitch for a professional first impression.
- **Vibe Threshold**: Adjust how strict the AI filter is for "suitability."

## 6. Advanced Configuration

### Adding Target Cities
Modify the `cities` list in `main.py`:
```python
cities = ["Detroit", "Berlin", "London", "Tokyo"]
```

### Adjusting the Vibe Filter
The threshold for a lead to appear on the dashboard is defined in `main.py`:
```python
if vibe_result['vibe_score'] >= 7: # Change this number to be more/less selective
```

---

## 6. Troubleshooting

- **Scraper Errors**: Venues like Resident Advisor have aggressive anti-bot protection. If results are empty, consider running from a different IP or updating the User-Agent in `src/scrapers/resident_advisor.py`.
- **Database Locked**: Ensure only one process is writing to the database at a time.
- **AI Not Configured**: If `OPENAI_API_KEY` is missing, the agent will assign a default score of 5 and a placeholder pitch.

---

## 7. Live Pilot & Environment Validation
The agent includes a suite of connectivity tests to ensure that external services (OpenAI, Proxies, SMTP) are reachable from your deployment environment.

To test your production environment:
```bash
python tests/test_live_connectivity.py
```

To execute a complete production-safe pilot run:
```bash
./pilot_run.sh
```

## 8. Extending the Agent
The system is modular. To add a new scraper (e.g., Eventbrite):
1.  Create a new file in `src/scrapers/`.
2.  Inherit from a base scraper class.
3.  Implement the `search_venues` method.
4.  Register it in `main.py`.
