# CHANGELOG

## [1.1.35] - 2024-05-31
### Added
- **Master Genre Dynamic Adaptation**: Refactored the entire AI and scouting pipeline to support any electronic music genre, removing hardcoded "psytrance" dependencies.
- **Configurable Active Genre**: The pipeline now uses the first genre in the `target_genres` configuration as the "Active Genre" for AI prompts and scraper queries.
- **Lead Genre Tracking**: Added `qualified_genre` to the leads schema to track which genre was used during qualification, now visible on the dashboard.
### Changed
- **AIEngine Robustness**: Updated core AI methods (`vibe_check`, `generate_pitch`, etc.) to utilize the new dynamic genre parameter.

## [1.1.34] - 2024-05-31
### Added
- **Manual Reply Dispatch**: Integrated a backend route and UI workflow for sending edited AI-drafted negotiation responses directly from the dashboard.
- **Interactive Dashboard Tooltips**: Enhanced the HITL Dashboard with informative Bootstrap tooltips for Vibe Scores, Success Probabilities, and Venue Traits.
### Fixed
- **Redundancy Cleanup**: Removed duplicate social context enrichment calls in the main pipeline.
- **Code Hygiene**: Fixed minor typos in SentimentAnalyzer and ensured proper imports in the dashboard app.

## [1.1.33] - 2024-05-31
### Added
- **Intelligent Reply Negotiation**: Introduced `generate_reply_draft` to AIEngine, enabling the agent to automatically draft professional responses to venue inquiries and interest.
- **Automated Draft Orchestration**: SentimentAnalyzer now triggers draft generation for positive sentiments, persisting them to the database for human review.
- **Dashboard Reply Management**: Enhanced the History view with interactive AI-drafted responses, allowing for rapid human-in-the-loop negotiation.

## [1.1.32] - 2024-05-31
### Added
- **Resident Advisor Enrichment Scraper**: Implemented detailed profile enrichment for RA venues, extracting actual websites, descriptions, and social links.
- **Enriched Outreach Pipeline**: Integrated RA enrichment into the main pipeline to improve data accuracy and qualification quality for leads sourced from RA.

## [1.1.31] - 2024-05-31
### Added
- **Success Probability Caching**: Implemented a persistence layer for outreach success probabilities to significantly reduce dashboard load times.
- **Automated Probability Backfill**: All existing leads are now pre-calculated and stored in the database.
### Fixed
- **E2E Test Robustness**: Resolved path resolution and CWD management issues in `tests/test_autonomous_pipeline_e2e.py` and `tests/test_protocol_e2e.py`, enabling full-cycle verification in sandboxed environments.

## [1.1.30] - 2024-05-30
### Added
- **Hardened Resident Advisor Scraper**: Refactored `ResidentAdvisorWebScraper` with Playwright to improve venue discovery and handle dynamic rendering on RA.co.
- **Enhanced Profile Discovery**: Now captures direct profile URLs during the discovery phase for deeper enrichment.

## [1.1.29] - 2024-05-30
### Added
- **Cluster-based Outreach Orchestration**: Enhanced the `TourPlanner` to generate unified regional residency pitches for venue hotspots.
- **Interactive Tour Dispatch**: Added a new UI workflow to the map dashboard allowing for the bulk dispatch of tour proposals to geographic clusters.
- **Unified Outreach Engine**: Expanded `OutreachEngine` to support coordinated multi-venue cluster dispatches.

## [1.1.28] - 2024-05-30
### Added
- **Sentiment-Driven Outreach Forecasting**: Introduced `OutreachPredictor` to calculate success probability for leads based on historical sentiment and AI-driven trait alignment.
- **Success Probability Visualization**: Integrated real-time success probability percentages into the HITL dashboard for prioritized lead review.

## [1.1.27] - 2024-05-30
### Added
- **Real-time Social Context Extraction**: Implemented `InstagramScraper` using Playwright to harvest live bio and activity snippets from venue profiles.
- **Enhanced AI Vibe Qualification**: Refined the `AIEngine` vibe-check prompt to prioritize social media signals and specific musical/atmospheric criteria for psytrance suitability.

## [1.1.26] - 2024-05-30
### Added
- **Architectural Consolidation**: Finalized the reconciliation of all distributed feature branches into a unified high-integrity production stream.
- **Enhanced System Traceability**: Completed the integration of the Version Audit infrastructure for real-time git-to-database synchronization.
- **Repository Refresh**: Executed the Executive Protocol for repository synchronization and intelligent merge.

## [1.1.24] - 2024-05-29
### Added
- **Contextual Media Matching**: Enhanced `AIEngine` to dynamically select the most relevant mix or visual from a new `media_library` based on venue atmosphere and technical specs.
- **Media Library Infrastructure**: Expanded `ConfigManager` to support a tagged library of promotional media for hyper-personalized outreach.
- **Social Vibe Enrichment**: Implemented `get_social_context` to incorporate mock Instagram "vibe" signals into the venue qualification process.

## [1.1.23] - 2024-05-27
### Added
- **AI-Driven Tour Routing**: Implemented `src/tour_planner.py` to suggest optimal multi-city tour sequences and strategies based on geographic clusters.
- **Venue Proximity Clustering**: Enhanced `src/analytics.py` with Haversine-based clustering to identify regional "hotspots" for promoters.
- **Enhanced Map Dashboard**: Added interactive hotspot visualization and frontend filters for vibe-score and pipeline-status on the Leaflet map.

## [1.1.22] - 2024-05-27
### Added
- **Geographic Intelligence**: Implemented `src/geocoding.py` using GPT-4o for zero-dependency venue coordinate resolution.
- **Interactive Lead Mapping**: Added `/map` view to the HITL Dashboard using Leaflet.js to visualize lead density and vibe-score heatmaps.
- **Geospatial Schema**: Extended `venues` table with `latitude` and `longitude` for persistent spatial intelligence.

## [1.1.21] - 2024-05-27
### Added
- **Safety Gate Verification**: Implemented `tests/test_sync_safety_gates.py` to formally verify push-abortion on system validation failure.
### Changed
- **Unit Test Isolation**: Hardened `test_sync_repo.py` to use `SKIP_SYNC_VALIDATION` for cleaner execution in simulated environments.

## [1.1.20] - 2024-05-27
### Added
- **Unified CI/CD Observability**: Integrated `PipelineMonitor` into the core `sync.yml` workflow, providing real-time granular reporting of CI validation and synchronization steps.
- **Milestone Finalization**: Completed the integration of the autonomous development and repository synchronization protocol across all tiered environments.

## [1.1.19] - 2024-05-27
### Added
- **Git Hook Hardening**: Updated `install_hooks.sh` to use dynamic root path resolution for the post-commit synchronization trigger.
### Changed
- **Pipeline Audit**: Conducted a final cross-environment stability audit, verifying all 30 tests in the Master Integrity Suite.
- **Typo Fixes**: Corrected spelling errors in the project changelog.

## [1.1.18] - 2024-05-27
### Added
- **Master Pipeline Unification**: Unified all major execution and deployment scripts (`start.sh`, `deploy_staging.sh`, `deploy_production.sh`) to use the hardened Master Integrity Suite (Pytest).
- **Production Observability**: Integrated production deployment monitoring via `PipelineMonitor`.
### Changed
- **Audit Hardening**: Refactored the daily integrity audit workflow to utilize Pytest for stress testing.

## [1.1.17] - 2024-05-27
### Added
- **Hardened Staging Environment**: Refactored `deploy_staging.sh` to use Pytest for standardized validation.
- **Unified Staging Monitoring**: Integrated `PipelineMonitor` into the staging deployment flow for consistent health reporting.
### Changed
- **Validation Standards**: Standardized all deployment scripts (staging/production) to utilize the hardened Master Integrity Suite.

## [1.1.16] - 2024-05-26
### Added
- **Unified Local Entry Point**: Refactored `start.sh` to use the Master Integrity Suite (Pytest) for all local system validations.
- **Protocol Observability**: Integrated local synchronization and testing events with `PipelineMonitor` for real-time dashboard reporting.
### Changed
- **Execution Standards**: Aligned local development execution flows with hardened CI/CD pipeline standards.

## [1.1.15] - 2024-05-26
### Added
- **CI Pipeline Monitoring**: Introduced `src/pipeline_monitor.py` for logging granular CI/CD execution data to the dashboard.
- **System Heartbeat**: Implemented `.github/workflows/heartbeat.yml` for automated 30-minute health and integrity checks.
- **Propagation Verification**: New `tests/test_end_to_end_propagation.py` validates bidirectional feature flow.
### Changed
- **Master Integrity Hardening**: Integrated code coverage (`pytest-cov`) into the primary synchronization workflow.

## [1.1.14] - 2024-05-26
### Added
- **Unified Protocol Synchronization**: Successfully reconciled all independent development streams into a single high-integrity production branch.
- **Master Versioning**: Established a unified global version string (v1.1.14) across all repository components.

## [1.1.13] - 2024-05-26
### Added
- **CI/CD Hardening**: Refactored `.github/workflows/sync.yml` to use Pytest for a more robust Master Integrity Suite execution.
- **Enhanced Test Coverage**: New `tests/test_trait_extraction.py` validates technical and atmospheric AI parsing.
### Changed
- **Dependency Management**: Standardized testing requirements with `pytest` and `pytest-mock` in `requirements.txt`.

## [1.1.12] - 2024-05-26
### Added
- **AI-Driven Trait Extraction**: Integrated GPT-4o powered extraction of sound system, lighting, and atmospheric traits from venue descriptions.
- **Hyper-Personalized Pitching**: Updated the AI engine to utilize extracted traits for bespoke outreach pitches.
- **Trait Visualization**: Enhanced the HITL Dashboard to display venue technical traits using specialized icons and badges.
- **Persistence Layer Update**: Added `extracted_traits` column to the `venues` table and updated `DatabaseManager`.

## [1.1.11] - 2024-05-26
### Added
- **Distributed Reconciliation**: Enhanced the sync protocol to support `--allow-unrelated-histories`, enabling reconciliation between independent autonomous agents.
- **Push Retry Logic**: Implemented "Retry-after-Rebase" loop in `sync_repo.py` to handle race conditions in distributed environments.
- **Multi-Agent Simulation**: New `tests/test_distributed_sync.py` validates concurrent modification handling.

## [1.1.10] - 2024-05-26
### Added
- **Staging Validation Suite**: New `tests/test_staging_readiness.py` verifies environment configuration, file permissions, and database connectivity.
- **Enhanced Staging Deployment**: `deploy_staging.sh` now logs automated health reporting events for release tracking.
- **Protocol Hardening**: Integrated staging release history into the autonomous audit cycle.

## [1.1.9] - 2024-05-26
### Added
- **Sync Reliability Monitoring**: New `ReliabilityMonitor` class analyzes synchronization history and calculates health KPIs.
- **Reliability Dashboard**: System page now displays 7-day sync success rate and failure metrics.
- **Repository Hygiene**: Automated `git remote prune origin` integration to keep the environment clean.
- **Staleness Detection**: Visual highlighting of branches that have not been reconciled for over 72 hours.
- **Performance Tracking**: Protocol now logs duration and timestamp for every synchronization event.

## [1.1.8] - 2024-05-24
### Added
- **Multi-Branch Health Reporting**: Synchronization protocol now logs granular branch-level status to the database.
- **Sync Integrity Dashboard**: Added a real-time branch health matrix to the System page.
- **Automated Integrity Auditing**: New GitHub Action for daily repository-wide unification audits.
- **Multi-Branch Stress Test**: Verified protocol stability with 5+ concurrent feature streams.

## [1.1.7] - 2024-05-24
### Added
- **Master Integrity Suite Integration**: Integrated 22 tests into the CI/CD pipeline and sync protocol.
- **Global Hub Expansion**: Backlog expanded to 15 cities with per-city analytics.
- **Scaling Resilience**: Verified multi-city resume logic and health tracking.

## [1.1.5] - 2024-05-24
### Added
- **Real-time Remote Synchronization**: Updated `sync_repo.py` to explicitly merge `origin/main` before local reconciliation, ensuring the agent always operates on the absolute latest remote state.
- **Concurrent Update Verification**: Implemented `tests/test_realtime_repo_updates.py` to validate protocol stability during simultaneous remote and local modifications.
- **Non-Interactive Git Operations**: Added `--no-edit` flags to all merge commands to prevent autonomous stalling in automated environments.

## [1.1.4] - 2024-05-24
### Added
- **Cross-Branch Consistency Verification**: Implemented `tests/test_cross_branch_consistency.py` to ensure database schema and system configuration changes are correctly reconciled across multiple active features.
- **Master Suite Expansion**: Integrated consistency verification into the Production Release script and CI workflows.

## [1.1.3] - 2024-05-24
### Added
- **Tiered Deployment Architecture**: Established Feature, Staging, and Production environments with dedicated GitHub Actions workflows.
- **Production Release Protocol**: Implemented `deploy_production.sh` which executes a **Master Integrity Suite** of 20+ tests before finalizing any release.
- **Automated Health Logging**: Deployment events are now automatically logged to the system health monitor.

## [1.1.2] - 2024-05-24
### Added
- **Live Connectivity Suite**: Implemented `tests/test_live_connectivity.py` to diagnose OpenAI, Proxy, and SMTP connectivity in production environments.
- **Pilot Execution Script**: Created `pilot_run.sh` for a safe, single-city autonomous validation cycle before full 24/7 deployment.

## [1.1.1] - 2024-05-24
### Added
- **Autonomous Pipeline E2E Test**: Implemented `tests/test_autonomous_pipeline_e2e.py` to verify the full cycle of code generation, repository synchronization, and pipeline execution.
- **Pipeline Health Integration**: Integrated `system_logs` reporting into the main pipeline execution for real-time dashboard monitoring.

## [1.1.0] - 2024-05-24
### Added
- **Repository Refresh**: Executed a full local/remote repository refresh protocol.
- **Structure Stabilization**: Reorganized root scripts and validated all pathing for autonomous execution.
- **Validated Build**: Unified root execution scripts (`start.sh`, `setup.sh`, `deploy_staging.sh`) and updated CI/CD workflows.

## [1.0.8] - 2024-05-24
### Added
- **Sentiment Analysis**: Integrated `SentimentAnalyzer` to categorize incoming venue replies (INTERESTED, REJECTED, INQUIRY).
- **Automation Pausing**: Updated `FollowUpEngine` to automatically stop follow-up cycles for leads that have received any human response.
- **Reply Dashboard**: Added a new section to the history view to display analyzed replies and their sentiment.

## [1.0.7] - 2024-05-24
### Added
- **Validated Push Protocol**: The synchronization script now executes critical integrity tests (`test_db_manager.py`, `test_ai_engine.py`, `test_smoke.py`) before pushing to the remote repository.
- **Hardened CI Pipeline**: Consolidated CI testing steps and integrated with the new validated push logic to protect branch integrity.

## [1.0.6] - 2024-05-24
### Added
- **Dashboard System UI**: New "System" page to monitor git status, branch info, and trigger repository synchronization via the web UI.
- **Integrated Sync Protocol**: Wired the backend sync logic to a Flask endpoint for manual human-in-the-loop control.
- **Dashboard Tests**: Added `tests/test_dashboard_sync.py` to verify UI-triggered protocols.

## [1.0.5] - 2024-05-24
### Added
- **Staging Environment**: Created `scripts/deploy_staging.sh` for isolated staging setup and testing.
- **CI Release Gates**: Implemented `.github/workflows/staging.yml` for automated staging validation on push.

## [1.0.4] - 2024-05-24
### Added
- **Multi-City Resume Logic**: Implemented `city_processing_log` to allow the pipeline to resume from where it left off.
- **Permanent Smoke Test**: Added `tests/test_smoke.py` for full end-to-end integration testing.
- **Robustness**: Improved `ConfigManager` error handling and added `is_city_processed` check to `main.py`.

## [1.0.3] - 2024-05-24
### Added
- **Follow-up Engine**: Implemented `src/follow_up_engine.py` for automated "nudge" outreach to non-responsive leads.
- **Persistence Tracking**: Added `last_outreach_at` and `follow_up_count` to the database schema.
- **AI Follow-up Generation**: New AIEngine method to generate concise, polite follow-up pitches.

## [1.0.2] - 2024-05-24
### Added
- **Proxy Rotation**: Implemented `ProxyRotator` in `base_scraper.py` and integrated it into all scrapers for bypassing anti-bot measures.
- **Outreach Engine**: Created `src/outreach_engine.py` for autonomous auto-approval and email dispatching.
- **System Integration**: Integrated the outreach cycle into the main pipeline and `start.sh`.

## [1.0.1] - 2024-05-24
### Added
- **Consistency Verification**: New step in `sync_repo.py` to verify that local and remote branches are perfectly synchronized after a push.
- **Enhanced Sync Tests**: Added test case for the new consistency verification logic.

## [1.0.0] - 2024-05-24
### Added
- **Production Milestone**: Full integration of autonomous development and synchronization protocol.
- **Unified Entry Point**: Reconciled all scripts and tests for high-integrity automated operation.
- **Verified Stability**: Completed extensive end-to-end testing of the synchronized development cycle.

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
