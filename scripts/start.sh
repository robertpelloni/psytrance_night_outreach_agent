#!/bin/bash
# Autonomous Development & Repository Synchronization Protocol: Start Script

echo "=== Protocol Triggered: $(date) ==="

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# 1. Activate environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 2. Run Repository Synchronization
echo "Step 1: Running Repository Synchronization..."
python3 scripts/sync_repo.py
if [ $? -ne 0 ]; then
    echo "CRITICAL: Synchronization failed. Check logs."
    exit 1
fi

# 3. Run Application Tests
echo "Step 2: Validating System Integrity..."
export PYTHONPATH=$PYTHONPATH:.
python3 tests/test_db_manager.py
python3 tests/test_ai_engine.py
if [ $? -ne 0 ]; then
    echo "CRITICAL: Application tests failed. Aborting pipeline."
    exit 1
fi

# 4. Handle Generator Mode (Optional)
if [ "$1" == "--generate" ] && [ -n "$2" ] && [ -n "$3" ]; then
    echo "Step 3: Launching Autonomous Scraper Generator..."
    # Usage: ./start.sh --generate "URL" "Source Name"
    python3 -c "from src.scraper_generator import ScraperGenerator; ScraperGenerator().generate_scraper('$2', '$3')"
    # After generation, we re-run sync to integrate the new code
    echo "Integrating new code..."
    python3 scripts/sync_repo.py
fi

# 5. Run Main Outreach Pipeline
echo "Step 4: Launching Outreach Pipeline..."
python3 main.py

echo "=== Protocol Session Finalized: $(date) ==="
