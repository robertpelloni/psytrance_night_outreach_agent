import json
import math
from src.ai_engine import AIEngine
from src.db_manager import DatabaseManager
from src.analytics import AnalyticsEngine

class TourPlanner:
    def __init__(self, db_path='database/outreach.db', ai=None):
        self.ai = ai or AIEngine()
        self.db = DatabaseManager(db_path=db_path)
        self.analytics = AnalyticsEngine(db_path=db_path)

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def get_circuit_route(self):
        """
        Calculates an optimal route connecting the centers of all identified venue clusters.
        Uses a nearest-neighbor approach starting from the cluster with the highest average vibe.
        """
        clusters = self.analytics.get_venue_clusters()
        if not clusters:
            return []

        # Start with the cluster that has the highest average vibe
        sorted_clusters = sorted(clusters, key=lambda x: x['avg_vibe'], reverse=True)
        unvisited = sorted_clusters[1:]

        route = [sorted_clusters[0]]
        current_cluster = sorted_clusters[0]

        while unvisited:
            # Find nearest neighbor
            nearest = min(
                unvisited,
                key=lambda c: self._haversine(
                    current_cluster['center']['lat'], current_cluster['center']['lon'],
                    c['center']['lat'], c['center']['lon']
                )
            )
            route.append(nearest)
            unvisited.remove(nearest)
            current_cluster = nearest

        return route

    def plan_optimized_tour(self, cluster_index=None):
        """
        Takes clusters of venues and uses AI to suggest an optimal
        visiting sequence and outreach strategy for a tour.
        If cluster_index is None, it plans a multi-city circuit across all clusters.
        """
        if not self.ai or not self.ai.client:
            return "Tour Planning requires an active AI Engine."

        clusters = self.analytics.get_venue_clusters()
        if not clusters:
            return "No clusters available for planning."

        # Fetch A/B variant stats to inform AI
        variant_stats = self.analytics.get_variant_stats()
        best_variant = None
        if variant_stats:
            best_variant = max(variant_stats.keys(), key=lambda k: variant_stats[k].get("conversion_rate", 0))

        if cluster_index is not None:
            if cluster_index >= len(clusters):
                return "Cluster index out of bounds."
            route_clusters = [clusters[cluster_index]]
            tour_scope = "a localized cluster"
        else:
            route_clusters = self.get_circuit_route()
            tour_scope = "a multi-city circuit across several regional clusters"

        # Format venues for AI
        venues_summary = []
        for i, cluster in enumerate(route_clusters):
            venues_summary.append(f"\nCluster {i+1} (Center Lat: {cluster['center']['lat']:.2f}, Lon: {cluster['center']['lon']:.2f}, Avg Vibe: {cluster['avg_vibe']:.1f}):")
            for v in cluster['venues']:
                venues_summary.append(f"- {v['name']} (Vibe: {v['vibe_score']}/10, Status: {v['pipeline_status']})")

        variant_advice = ""
        if best_variant:
            variant_advice = f"\n4. Note: Analytics show our '{best_variant}' pitch variant converts best. Tailor the suggested outreach strategy to align with the tone of this variant."

        prompt = f"""
        Plan an optimal psytrance tour route for {tour_scope} based on the following venues:
        {chr(10).join(venues_summary)}

        Provide:
        1. An optimal visiting sequence (route) that minimizes travel time between venues and clusters.
        2. A cohesive 'tour pitch' strategy that emphasizes the connection between these venues and our multi-city presence.
        3. Logistics advice for this specific route. {variant_advice}

        Return as a structured recommendation.
        """

        try:
            response = self.ai.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error planning tour: {e}"

    def generate_cluster_pitch(self, cluster_index=0):
        """Generates a unified tour residency pitch for all venues in a cluster."""
        if not self.ai or not self.ai.client:
            return None

        clusters = self.analytics.get_venue_clusters()
        if not clusters or cluster_index >= len(clusters):
            return None

        cluster = clusters[cluster_index]
        venues_list = cluster['venues']
        venues_names = ", ".join([v['name'] for v in venues_list])

        prompt = f"""
        Write a professional cold email proposing a psytrance 'regional residency tour'.
        We are reaching out to a group of top-tier venues in this region: {venues_names}.

        The pitch should:
        1. Propose a coordinated series of events across these specific venues.
        2. Explain the benefits of a regional tour (shared promotion, reduced travel costs, building a local scene).
        3. Reference the high 'vibe alignment' of these venues.

        This will be sent individually to each venue, but will mention the other venues in the cluster to show the scale of the tour.

        Tone: Professional, ambitious, and scene-building.
        """
        try:
            response = self.ai.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating cluster pitch: {e}")
            return None

if __name__ == "__main__":
    planner = TourPlanner()
    print(planner.plan_optimized_tour())
