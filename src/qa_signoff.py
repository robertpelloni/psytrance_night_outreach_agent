import sys
import os

# Ensure project root is in sys.path when run directly
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db_manager import DatabaseManager

def qa_signoff(run_id, component, status):
    """
    Final QA sign-off utility.
    Verifies system readiness and logs a specialized event.
    """
    db = DatabaseManager()

    # Check for recent critical failures
    logs = db.get_latest_system_logs(limit=50)
    critical_failures = [l for l in logs if l['status'] == 'FAILURE' and l['component'] in ['PIPELINE', 'SYNC']]

    message = f"QA Sign-off for Run: {run_id} | Component: {component} | Status: {status}"
    if critical_failures:
        message += f" | WARNING: Found {len(critical_failures)} recent failures in logs."
        print(f"QA_SIGNOFF WARNING: {len(critical_failures)} recent critical failures detected.")
    else:
        message += " | All recent critical components reported SUCCESS."
        print("QA_SIGNOFF: Clean bill of health detected.")

    db.log_system_event("QA_SIGNOFF", status, message)
    print(f"QA Sign-off logged successfully for {run_id}.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 src/qa_signoff.py <run_id> <component> <status>")
        sys.exit(1)

    run_id = sys.argv[1]
    component = sys.argv[2]
    status = sys.argv[3]

    qa_signoff(run_id, component, status)
