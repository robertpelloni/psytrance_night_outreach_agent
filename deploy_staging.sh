#!/bin/bash
# Autonomous Development Protocol: Staging Deployment & Validation Script

echo "=== STAGING DEPLOYMENT START: $(date) ==="

# 1. Environment Setup
echo "Step 1: Setting up environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi
pip install -r requirements.txt
playwright install chromium

# 2. Staging Database Initialization
echo "Step 2: Initializing staging database..."
export DB_PATH="database/staging_outreach.db"
# DatabaseManager will automatically create it based on schema.sql
python3 -c "from src.db_manager import DatabaseManager; DatabaseManager(db_path='$DB_PATH')"

# 3. Run End-to-End Integration Tests
echo "Step 3: Running End-to-End Integration Tests..."
export PYTHONPATH=$PYTHONPATH:.
python3 tests/test_smoke.py
if [ $? -ne 0 ]; then
    echo "ERROR: Staging smoke tests failed! Aborting."
    exit 1
fi

python3 tests/test_protocol_e2e.py
if [ $? -ne 0 ]; then
    echo "ERROR: Staging protocol tests failed! Aborting."
    exit 1
fi

# 4. Final Validation Summary
echo "=== STAGING DEPLOYMENT SUCCESSFUL: $(date) ==="
echo "System is verified for staging at $DB_PATH."
