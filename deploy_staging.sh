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

# 3. Run Master Integrity Suite (v1.1.7)
echo "Step 3: Running Master Integrity Suite..."
export PYTHONPATH=$PYTHONPATH:.
python3 -m unittest discover tests
if [ $? -ne 0 ]; then
    echo "ERROR: Master Integrity Suite failed in staging! Aborting."
    exit 1
fi

python3 test_sync_repo.py
if [ $? -ne 0 ]; then
    echo "ERROR: Sync protocol verification failed in staging! Aborting."
    exit 1
fi

# 4. Final Validation Summary
echo "=== STAGING DEPLOYMENT SUCCESSFUL: $(date) ==="
echo "System is verified for staging at $DB_PATH."
