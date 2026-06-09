CREATE TABLE IF NOT EXISTS venues (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    website TEXT UNIQUE,
    google_rating REAL,
    tags TEXT, -- JSON string or comma-separated tags
    raw_about_text TEXT,
    extracted_traits TEXT, -- JSON blob of sound/lighting/vibe traits
    latitude REAL,
    longitude REAL,
    image_url TEXT,
    visual_description TEXT,
    address TEXT,
    phone TEXT,
    venue_type TEXT,
    capacity INTEGER,
    neighborhood TEXT,
    source TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS venue_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    instagram_handle TEXT UNIQUE,
    booking_page_url TEXT,
    FOREIGN KEY(venue_id) REFERENCES venues(id)
);

CREATE TABLE IF NOT EXISTS outreach_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id TEXT UNIQUE,
    vibe_score INTEGER,
    qualification_justification TEXT,
    generated_pitch TEXT,
    pipeline_status TEXT DEFAULT 'PENDING_QUALIFICATION', -- PENDING_QUALIFICATION, PENDING_REVIEW, APPROVED, REJECTED, SENT, REJECTED
    qualified_genre TEXT,
    pitch_variant TEXT, -- A/B testing variant (e.g., 'Professional', 'Underground', 'Technical')
    last_outreach_at TIMESTAMP,
    follow_up_count INTEGER DEFAULT 0,
    success_probability REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(venue_id) REFERENCES venues(id)
);

CREATE TABLE IF NOT EXISTS city_processing_log (
    city TEXT PRIMARY KEY,
    last_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT -- COMPLETED, FAILED
);

CREATE TABLE IF NOT EXISTS lead_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    content TEXT NOT NULL,
    sentiment TEXT, -- INTERESTED, REJECTED, INQUIRY, OOO, UNKNOWN
    draft_response TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(lead_id) REFERENCES outreach_leads(id)
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL, -- SYNC, DISCOVERY, OUTREACH
    status TEXT NOT NULL, -- SUCCESS, FAILURE
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS version_audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_hash TEXT NOT NULL,
    author TEXT,
    timestamp DATETIME,
    version_string TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT, -- RUNNING, COMPLETED, FAILED
    city_count INTEGER DEFAULT 0,
    venues_found INTEGER DEFAULT 0,
    leads_generated INTEGER DEFAULT 0,
    error_message TEXT
);
