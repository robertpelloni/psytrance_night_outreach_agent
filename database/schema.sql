CREATE TABLE IF NOT EXISTS venues (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    website TEXT UNIQUE,
    google_rating REAL,
    tags TEXT, -- JSON string or comma-separated tags
    raw_about_text TEXT
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(venue_id) REFERENCES venues(id)
);
