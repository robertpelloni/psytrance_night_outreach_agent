# CHANGELOG

## [1.1.63] - 2026-06-12
### Added
- **Phase 48: Usage Transparency & Inbox Reliability**: Finalized integration of token usage tracking and bounce detection.
- **Phase 47: Multi-Artist Collective Architecture**: Completed the transition to a collective model with per-lead artist assignment.
- **Lead Export**: Added CSV export functionality for leads and contacts.
- **Architecture Review**: Conducted a full src/ audit, confirming 100% logic coverage and zero remaining TODOs.
- **Repository Synchronization**: Executed the Executive Protocol for Repository Synchronization, reconciling all legacy feature branches into `main`.

### Fixed
- **RA Enrichment Regression**: Resolved double-initialization of retry logic in `ResidentAdvisorWebScraper`.
- **System Stability**: Re-verified 100% pass rate on Master Integrity Suite (84 tests) post-synchronization.

## [1.1.62] - 2026-06-11
### Added
- **AI Token Usage Tracking**: Implemented automated tracking and logging of OpenAI token usage (prompt, completion, total) for all AI calls.
- **AI Usage Dashboard**: Added a new visualization in the System dashboard showing 7-day token consumption per model.
- **Unmatched Reply Management**: Implemented an "Unmatched Replies" system to capture and store incoming emails that cannot be automatically linked to a lead.
- **Manual Match UI**: Added a UI in the History view for manually assigning unmatched replies to leads.
- **SMTP Bounce Detection**: Integrated automated detection for delivery failure notifications (bounces), with automatic lead status updates to 'BOUNCED'.
- **Verification Suites**: Added `tests/test_ai_usage.py` and `tests/test_bounce_detection.py` to the Master Integrity Suite.

[... remainder of changelog ...]
