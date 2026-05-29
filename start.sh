#!/bin/bash
# Autonomous Development & Repository Synchronization Protocol: Start Script

echo "=== Protocol Triggered: $(date) ==="

# Ensure we are in the project root
cd "$(dirname "$0")"

# 1. Activate environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 2. Run Repository Synchronization
echo "Step 1: Running Repository Synchronization..."
python3 sync_repo.py
SYNC_RES=$?
if [ $SYNC_RES -ne 0 ]; then
    echo "CRITICAL: Synchronization failed. Check logs."
    python3 src/pipeline_monitor.py "local-$(date +%s)" "LOCAL_SYNC" "FAILURE"
    exit 1
else
    python3 src/pipeline_monitor.py "local-$(date +%s)" "LOCAL_SYNC" "SUCCESS"
fi

# 3. Run Application Tests (Master Integrity Suite)
echo "Step 2: Validating System Integrity..."
export PYTHONPATH=$PYTHONPATH:.
python3 -m pytest
TEST_RES=$?
if [ $TEST_RES -ne 0 ]; then
    echo "CRITICAL: Master Integrity Suite failed. Aborting pipeline."
    python3 src/pipeline_monitor.py "local-$(date +%s)" "LOCAL_TEST" "FAILURE"
    exit 1
else
    python3 src/pipeline_monitor.py "local-$(date +%s)" "LOCAL_TEST" "SUCCESS"
fi

# 4. Handle Generator Mode (Optional)
if [ "$1" == "--generate" ] && [ -n "$2" ] && [ -n "$3" ]; then
    echo "Step 3: Launching Autonomous Scraper Generator..."
    # Usage: ./start.sh --generate "URL" "Source Name"
    python3 -c "from src.scraper_generator import ScraperGenerator; ScraperGenerator().generate_scraper('$2', '$3')"
    # After generation, we re-run sync to integrate the new code
    echo "Integrating new code..."
    python3 sync_repo.py
fi

# 5. Run Main Outreach Pipeline
echo "Step 4: Launching Outreach Pipeline..."
python3 main.py

# 6. Optional: Start Outreach Engine in background if not already running
# pgrep -f "src/outreach_engine.py" > /dev/null || python3 src/outreach_engine.py > outreach.log 2>&1 &

echo "=== Protocol Session Finalized: $(date) ==="
