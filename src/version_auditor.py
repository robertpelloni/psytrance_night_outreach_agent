import subprocess
import os
import sys
from src.db_manager import DatabaseManager

class VersionAuditor:
    def __init__(self, db_path=None):
        self.db = DatabaseManager(db_path=db_path)

    def harvest_git_logs(self, limit=50):
        """Extracts git commit history and persists it to the version_audit_trail."""
        try:
            # Format: hash | author | date | subject
            cmd = ["git", "log", f"-n {limit}", "--format=%H|%an|%ai|%s"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error harvesting git logs: {result.stderr}")
                return

            commits = result.stdout.splitlines()

            # Get current version from file
            version = "unknown"
            version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION.md')
            if os.path.exists(version_path):
                with open(version_path, 'r') as f:
                    version = f.read().strip()

            with self.db._get_connection() as conn:
                for commit in commits:
                    parts = commit.split('|')
                    if len(parts) < 4: continue

                    h, author, date, subject = parts

                    # Deduplicate: Check if hash exists
                    exists = conn.execute("SELECT 1 FROM version_audit_trail WHERE commit_hash = ?", (h,)).fetchone()
                    if not exists:
                        query = """
                        INSERT INTO version_audit_trail (commit_hash, author, timestamp, version_string, summary)
                        VALUES (?, ?, ?, ?, ?)
                        """
                        conn.execute(query, (h, author, date, version if version in subject else None, subject))

            print(f"Audit trail synchronized: {len(commits)} commits processed.")
        except Exception as e:
            print(f"Auditor Error: {e}")

if __name__ == "__main__":
    auditor = VersionAuditor()
    auditor.harvest_git_logs()
