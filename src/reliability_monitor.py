import sqlite3
import os
from datetime import datetime, timedelta

class ReliabilityMonitor:
    def __init__(self, db_path='database/outreach.db'):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_sync_health_stats(self):
        query = """
        SELECT status, count(*) as count
        FROM system_logs
        WHERE component = 'SYNC'
        AND created_at >= datetime('now', '-7 days')
        GROUP BY status
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            rows = cursor.fetchall()

        stats = {row['status']: row['count'] for row in rows}
        total = sum(stats.values())
        success_rate = (stats.get('SUCCESS', 0) / total * 100) if total > 0 else 0

        return {
            "total_syncs": total,
            "success_rate": round(success_rate, 1),
            "failures": stats.get('FAILURE', 0)
        }

    def get_stale_branches(self, threshold_hours=72):
        import subprocess
        branches = subprocess.getoutput("git branch -r --format='%(refname:short)|%(authordate:iso8601)'").splitlines()
        stale = []
        now = datetime.now()

        for b in branches:
            if '|' not in b: continue
            name, date_str = b.split('|')
            if 'origin/main' in name or 'HEAD' in name: continue

            # Simple ISO parse
            try:
                dt = datetime.fromisoformat(date_str.split(' ')[0] + ' ' + date_str.split(' ')[1])
                if (now - dt).total_seconds() > (threshold_hours * 3600):
                    stale.append({"name": name.replace('origin/', ''), "last_commit": date_str})
            except:
                continue
        return stale

if __name__ == "__main__":
    monitor = ReliabilityMonitor()
    print(monitor.get_sync_health_stats())
