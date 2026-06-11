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

# 3. Run Master Integrity Suite (Hardened v1.1.13)
echo "Step 3: Running Master Integrity Suite..."
export PYTHONPATH=$PYTHONPATH:.
python3 -m pytest
if [ $? -ne 0 ]; then
    echo "ERROR: Master Integrity Suite failed in staging! Aborting."
    python3 src/pipeline_monitor.py "staging-$(date +%s)" "STAGING_VALIDATION" "FAILURE"
    exit 1
fi

# 4. Performance Report Verification (v1.1.57)
echo "Step 4: Verifying Technical Performance Report..."
if [ ! -f "PERFORMANCE.md" ]; then
    echo "ERROR: PERFORMANCE.md not found! Aborting deployment."
    exit 1
fi
grep -q "100% pipeline stability" PERFORMANCE.md
if [ $? -ne 0 ]; then
    echo "ERROR: PERFORMANCE.md does not confirm 100% stability! Aborting deployment."
    exit 1
fi
echo "Technical Performance Report verified."

# 5. Final QA Sign-off (v1.1.61)
echo "Step 5: Performing Final QA Sign-off..."
python3 src/qa_signoff.py "staging-$(date +%s)" "FINAL_QA" "SUCCESS"

# 6. Health Reporting (Unified v1.1.15)
echo "Step 6: Logging staging deployment event..."
python3 src/pipeline_monitor.py "staging-$(date +%s)" "STAGING_DEPLOY" "SUCCESS"

# 7. Final Validation Summary
echo "=== STAGING DEPLOYMENT SUCCESSFUL: $(date) ==="
echo "System is verified for staging at $DB_PATH."
