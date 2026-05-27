#!/bin/bash
# Autonomous Development Protocol: Production Deployment & Final Validation
# This script represents the final quality gate before full autonomous operation.

echo "=== PRODUCTION DEPLOYMENT START: $(date) ==="

# 1. Environment Refresh
echo "Step 1: Refreshing production environment..."
./setup.sh

# 2. Final Repository Synchronization (Optional for Sandbox)
echo "Step 2: Executing final repository reconciliation..."
export SKIP_SYNC_VALIDATION=1 # We run validation separately in Step 3
# In sandbox, sync might fail due to lack of remote push access, we warn but continue
python3 sync_repo.py || echo "Warning: Sync script returned non-zero. Continuing with local validation."

# 3. Comprehensive Master Validation (Hardened v1.1.13)
echo "Step 3: Running Master Integrity Suite..."
export PYTHONPATH=$PYTHONPATH:.
python3 -m pytest
if [ $? -ne 0 ]; then
    echo "ERROR: Integrity tests failed! Production state compromised. Aborting."
    python3 src/pipeline_monitor.py "prod-$(date +%s)" "PRODUCTION_VALIDATION" "FAILURE"
    exit 1
fi

# 4. Production Health Logging (Unified v1.1.15)
echo "Step 4: Logging deployment event..."
python3 src/pipeline_monitor.py "prod-$(date +%s)" "PRODUCTION_DEPLOY" "SUCCESS"

echo "=== PRODUCTION DEPLOYMENT SUCCESSFUL: $(date) ==="
echo "Autonomous Agent is now operational in production mode."
