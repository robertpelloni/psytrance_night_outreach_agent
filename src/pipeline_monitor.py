import os
import sys
import time
from src.db_manager import DatabaseManager

class PipelineMonitor:
    def __init__(self, db_path=None):
        self.db = DatabaseManager(db_path=db_path)

    def log_ci_run(self, run_id, component, status, duration=None, coverage=None):
        message = f"Run ID: {run_id}"
        if duration:
            message += f" | Duration: {duration}s"
        if coverage:
            message += f" | Coverage: {coverage}%"

        self.db.log_system_event(component, status, message)

if __name__ == "__main__":
    # Allow CLI usage for GitHub Actions
    if len(sys.argv) < 4:
        print("Usage: python3 src/pipeline_monitor.py <run_id> <component> <status> [duration] [coverage]")
        sys.exit(1)

    run_id = sys.argv[1]
    component = sys.argv[2]
    status = sys.argv[3]
    duration = sys.argv[4] if len(sys.argv) > 4 else None
    coverage = sys.argv[5] if len(sys.argv) > 5 else None

    monitor = PipelineMonitor()
    monitor.log_ci_run(run_id, component, status, duration, coverage)
    print(f"Logged CI run {run_id} for {component} with status {status}")
