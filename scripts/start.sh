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

# 4. Run Main Outreach Pipeline
echo "Step 3: Launching Outreach Pipeline..."
python3 main.py

echo "=== Protocol Session Finalized: $(date) ==="
