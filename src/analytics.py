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

    def get_venue_clusters(self, radius_km=50):
        """
        Identifies clusters of venues within a specific radius.
        Simple implementation using Haversine or simple distance for nearby venues.
        """
        query = """
        SELECT v.id, v.name, v.latitude, v.longitude, l.vibe_score, l.pipeline_status
        FROM venues v
        JOIN outreach_leads l ON v.id = l.venue_id
        WHERE v.latitude IS NOT NULL AND v.longitude IS NOT NULL
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            venues = [dict(row) for row in conn.execute(query).fetchall()]

        if not venues:
            return []

        clusters = []
        visited = set()

        import math

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371 # Earth radius
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        for i, v1 in enumerate(venues):
            if v1['id'] in visited:
                continue

            current_cluster = [v1]
            visited.add(v1['id'])

            for j, v2 in enumerate(venues):
                if v1['id'] == v2['id'] or v2['id'] in visited:
                    continue

                dist = haversine(v1['latitude'], v1['longitude'], v2['latitude'], v2['longitude'])
                if dist <= radius_km:
                    current_cluster.append(v2)
                    visited.add(v2['id'])

            if len(current_cluster) > 1:
                clusters.append({
                    "center": {
                        "lat": sum(v['latitude'] for v in current_cluster) / len(current_cluster),
                        "lon": sum(v['longitude'] for v in current_cluster) / len(current_cluster)
                    },
                    "venue_count": len(current_cluster),
                    "venues": current_cluster,
                    "avg_vibe": sum(v['vibe_score'] for v in current_cluster) / len(current_cluster)
                })

        return sorted(clusters, key=lambda x: x['venue_count'], reverse=True)
