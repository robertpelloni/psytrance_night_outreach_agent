import sqlite3
import os

class AnalyticsEngine:
    def __init__(self, db_path='database/outreach.db'):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_summary_stats(self):
        stats = {}
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row

            # Total Venues
            res = conn.execute("SELECT count(*) FROM venues").fetchone()
            stats['total_venues'] = res[0]

            # Total Leads by Status
            res = conn.execute("SELECT pipeline_status, count(*) as count FROM outreach_leads GROUP BY pipeline_status").fetchall()
            stats['status_breakdown'] = {row['pipeline_status']: row['count'] for row in res}

            # Average Vibe Score
            res = conn.execute("SELECT AVG(vibe_score) FROM outreach_leads WHERE vibe_score IS NOT NULL").fetchone()
            stats['avg_vibe_score'] = round(res[0], 2) if res[0] else 0

            # Cities Distribution
            res = conn.execute("SELECT city, count(*) as count FROM venues GROUP BY city").fetchall()
            stats['city_distribution'] = {row['city']: row['count'] for row in res}

        return stats

    def get_approval_rate(self):
        with self._get_connection() as conn:
            # Approval Rate = (SENT + APPROVED) / (SENT + APPROVED + REJECTED)
            query = """
            SELECT
                SUM(CASE WHEN pipeline_status IN ('SENT', 'APPROVED') THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN pipeline_status IN ('SENT', 'APPROVED', 'REJECTED') THEN 1 ELSE 0 END) as total
            FROM outreach_leads
            """
            res = conn.execute(query).fetchone()
            if res[1] and res[1] > 0:
                return round((res[0] / res[1]) * 100, 1)
            return 0
