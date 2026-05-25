# CHANGELOG

## [0.9.0] - 2024-05-24
### Added
- **Autonomous Dev Workflow**: Integrated scraper generation into the unified execution script (`start.sh --generate`).
- **Dev Cycle E2E Test**: New `tests/test_autonomous_dev_e2e.py` verifying the full code-gen-to-sync cycle.
- **Unified CI Gating**: System now validates autonomous development logic before deployment.

## [0.8.0] - 2024-05-24
### Added
- **Centralized Configuration**: Implemented `ConfigManager` to handle target cities, genres, and project links.
- **Settings Dashboard**: New page to manage project configurations and branding links dynamically.
- **EPK Integration**: AI-generated pitches now include EPK and showcase mix links for increased professionalism.

## [0.7.0] - 2024-05-24
### Added
- **Outreach Analytics**: New dashboard view for tracking approval rates, status breakdowns, and city distributions.
- **Social Media Helper**: Added Instagram handle display and "Copy for DM" clipboard functionality to pending leads.
- **Enhanced Data Retrieval**: Improved SQL queries to fetch contact info directly with pending leads.

## [0.6.0] - 2024-05-24
### Added
- **AI Conflict Resolution**: Integrated OpenAI into the synchronization script to automatically resolve git merge conflicts.
- **Improved Sync Tests**: Added test cases for AI-powered conflict resolution and refined branch discovery logic.

## [0.5.1] - 2024-05-24
### Added
- Created `scripts/setup.sh` and `scripts/start.sh` for unified execution.
- Added `tests/test_protocol_e2e.py` for end-to-end protocol verification.

## [0.5.0] - 2024-05-24
### Added
- **AI Scraper Generation**: Integrated `src/scraper_generator.py` for real-time creation of scrapers via OpenAI.
- **Dynamic Scraper Loading**: Orchestrator now automatically discovers and runs all scrapers in `src/scrapers/`.
- **Source Management UI**: Added a new dashboard page to manage and generate new scraping sources.

## [0.4.3] - 2024-05-24
### Changed
- Enhanced synchronization script with detailed logging and improved error reporting.
- Added conflict handling test cases to the synchronization test suite.

## [0.4.2] - 2024-05-24
### Added
- Comprehensive application tests (`tests/test_db_manager.py`, `tests/test_ai_engine.py`).
- Integrated application tests into the CI pipeline.

## [0.4.1] - 2024-05-24
### Added
- Automated test suite for the repository synchronization protocol (`scripts/test_sync_repo.py`).
- Integrated synchronization tests into the CI pipeline.

## [0.4.0] - 2024-05-24
### Changed
- Refined database schema with UNIQUE constraints for venues and leads.
- Improved pipeline orchestration to perform enrichment before vibe checks.
- Refactored synchronization script for more robust branch discovery.

## [0.3.1] - 2024-05-24
### Changed
- Configured repository synchronization workflow to trigger on pushes to `main`.

## [0.3.0] - 2024-05-24
### Added
- Created a comprehensive User Manual (`MANUAL.md`).
- Implemented User-Agent rotation to help avoid rate limiting and detection.
- Added a "History" view to the dashboard for sent and rejected leads.

## [0.2.2] - 2024-05-24
### Added
- Integrated repository synchronization protocol into CI via GitHub Actions.
- Created `scripts/sync_repo.py` for automated branch merging and submodule updates.

## [0.2.1] - 2024-05-24
### Added
- Initialized core project structure.
- Implemented SQLite schema and DatabaseManager.
- Created AIEngine for vibe checks and pitch generation.
- Added basic Flask dashboard for HITL review.
- Established documentation standards (VISION, MEMORY, etc.).

## [0.1.0] - 2024-05-24
### Added
- Project concept and structural blueprint.
