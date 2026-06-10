import sqlite3
import os

class AnalyticsEngine:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.getenv("DB_PATH") or 'database/outreach.db'

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

    def get_conversion_funnel(self):
        """Calculates conversion metrics for each stage of the pipeline."""
        funnel = {}
        with self._get_connection() as conn:
            # 1. Discovered (Total Venues)
            res = conn.execute("SELECT count(*) FROM venues").fetchone()
            funnel['discovered'] = res[0]

            # 2. Qualified (Vibe Score >= threshold, usually PENDING_REVIEW or beyond)
            res = conn.execute("SELECT count(*) FROM outreach_leads WHERE vibe_score >= 6").fetchone()
            funnel['qualified'] = res[0]

            # 3. Pitched (SENT status)
            res = conn.execute("SELECT count(*) FROM outreach_leads WHERE pipeline_status IN ('SENT', 'BOOKED', 'LOST')").fetchone()
            funnel['pitched'] = res[0]

            # 4. Replied (Has at least one reply)
            res = conn.execute("SELECT count(DISTINCT lead_id) FROM lead_replies").fetchone()
            funnel['replied'] = res[0]

            # 5. Booked (BOOKED status)
            res = conn.execute("SELECT count(*) FROM outreach_leads WHERE pipeline_status = 'BOOKED'").fetchone()
            funnel['booked'] = res[0]

        return funnel

    def get_scene_health(self):
        """Calculates key performance indicators for the overall outreach effort."""
        kpis = {}
        with self._get_connection() as conn:
            # Response Rate: Replied / Pitched
            pitched = conn.execute("SELECT count(*) FROM outreach_leads WHERE pipeline_status IN ('SENT', 'BOOKED', 'LOST')").fetchone()[0]
            replied = conn.execute("SELECT count(DISTINCT lead_id) FROM lead_replies").fetchone()[0]
            kpis['response_rate'] = round((replied / pitched * 100), 1) if pitched > 0 else 0

            # Booking Rate: Booked / Replied
            booked = conn.execute("SELECT count(*) FROM outreach_leads WHERE pipeline_status = 'BOOKED'").fetchone()[0]
            kpis['booking_rate'] = round((booked / replied * 100), 1) if replied > 0 else 0

            # Interested Rate: Leads with at least one INTERESTED reply / Pitched
            interested = conn.execute("SELECT count(DISTINCT lead_id) FROM lead_replies WHERE sentiment = 'INTERESTED'").fetchone()[0]
            kpis['interested_rate'] = round((interested / pitched * 100), 1) if pitched > 0 else 0

        return kpis

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

    def get_variant_stats(self):
        """Calculates conversion metrics per pitch variant."""
        query = """
        SELECT
            l.pitch_variant,
            COUNT(l.id) as total_leads,
            SUM(CASE WHEN l.pipeline_status IN ('SENT', 'APPROVED') THEN 1 ELSE 0 END) as sent_or_approved,
            SUM(CASE WHEN r.sentiment = 'INTERESTED' THEN 1 ELSE 0 END) as interested_replies
        FROM outreach_leads l
        LEFT JOIN lead_replies r ON l.id = r.lead_id
        WHERE l.pitch_variant IS NOT NULL
        GROUP BY l.pitch_variant
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()

            stats = {}
            for row in rows:
                variant = row['pitch_variant']
                total = row['total_leads']
                sent = row['sent_or_approved']
                interested = row['interested_replies'] or 0

                # Conversion rate = interested / sent (if any sent)
                conv_rate = round((interested / sent * 100), 1) if sent > 0 else 0

                stats[variant] = {
                    "total": total,
                    "sent": sent,
                    "interested": interested,
                    "conversion_rate": conv_rate
                }
            return stats

    def get_venue_warmth(self, venue_id):
        """
        Calculates a 'warmth' score (0-100) based on interaction recency and sentiment.
        """
        warmth = 0
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row

            # Fetch lead and replies
            lead = conn.execute("SELECT * FROM outreach_leads WHERE venue_id = ?", (venue_id,)).fetchone()
            if not lead: return 0

            replies = conn.execute("SELECT * FROM lead_replies WHERE lead_id = ? ORDER BY received_at DESC", (lead['id'],)).fetchall()

            if not replies:
                # Cold: If sent but no reply, check recency
                if lead['pipeline_status'] == 'SENT':
                    warmth = 20
                return warmth

            # Base warmth for having a reply
            warmth = 40

            # Most recent sentiment bonus
            latest = replies[0]
            if latest['sentiment'] == 'INTERESTED':
                warmth += 40
            elif latest['sentiment'] == 'INQUIRY':
                warmth += 20
            elif latest['sentiment'] == 'REJECTED':
                warmth = 5
                return warmth

            # Recency bonus (within 7 days)
            import datetime
            try:
                # SQL format is YYYY-MM-DD HH:MM:SS
                received_at = datetime.datetime.strptime(latest['received_at'], "%Y-%m-%d %H:%M:%S")
                delta = datetime.datetime.now() - received_at
                if delta.days < 7:
                    warmth += 20
            except:
                pass

        return min(warmth, 100)
