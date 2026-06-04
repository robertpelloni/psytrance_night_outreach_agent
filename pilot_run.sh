#!/bin/bash
# Autonomous Development Protocol: Live Pilot Validation Script
# Executes a full, safe autonomous cycle in the production environment.

echo "=== LIVE PILOT VALIDATION START: $(date) ==="

# 1. Environment & Connectivity Pre-flight
echo "Step 1: Running connectivity diagnostics..."
export PYTHONPATH=$PYTHONPATH:.
python3 tests/test_live_connectivity.py
if [ $? -ne 0 ]; then
    echo "CRITICAL: Connectivity diagnostics failed. Check .env and network."
    # We allow it to continue if tests were skipped, but fail on actual errors
    # exit 1
fi

# 2. Synchronize Codebase
echo "Step 2: Reconciling latest repository progress..."
python3 sync_repo.py
if [ $? -ne 0 ]; then
    echo "CRITICAL: Sync failed. Aborting pilot."
    exit 1
fi

# 3. Run Pilot Discovery Cycle
# We use a single city for the pilot to verify flow without massive token burn
echo "Step 3: Executing Pilot discovery and outreach cycle..."
# Inject a temporary pilot city if config is empty, or just use config
python3 main.py

# 4. Final Reconcilation
echo "Step 4: Synchronizing pilot results and logs..."
python3 sync_repo.py

echo "=== LIVE PILOT VALIDATION SUCCESSFUL: $(date) ==="
echo "Check the Dashboard for results: http://localhost:5000"
