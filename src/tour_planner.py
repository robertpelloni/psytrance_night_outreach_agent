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

    def get_circuit_route(self, clusters=None, method='dbscan', min_vibe=6.5):
        """
        Calculates an optimal route connecting the centers of all identified venue clusters.
        Uses a nearest-neighbor approach starting from the Detroit hub (or highest average vibe cluster).
        """
        if clusters is None:
            clusters = self.analytics.get_venue_clusters(method=method, min_vibe=min_vibe)
        if not clusters:
            return []

        # Detroit approximate coordinates: 42.3314, -83.0458
        detroit_lat, detroit_lon = 42.3314, -83.0458

        detroit_clusters = [
            c for c in clusters
            if any((v.get('city', '') or '').lower() == 'detroit' for v in c.get('venues', [])) or
               self._haversine(detroit_lat, detroit_lon, c['center']['lat'], c['center']['lon']) < 80
        ]
        start_cluster = detroit_clusters[0] if detroit_clusters else max(clusters, key=lambda x: x.get('avg_vibe', 0))

        unvisited = [c for c in clusters if c != start_cluster]
        route = [start_cluster]
        current_cluster = start_cluster

        while unvisited:
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

    def compute_circuit_logistics(self, route_clusters=None, method='dbscan', min_vibe=6.5, artist_id=None):
        """
        Calculates operational tour transit metrics across the circuit:
        - Total transit distance (km)
        - Estimated driving hours (at 85 km/h highway nominal transit speed)
        - Recommended rest days (1 rest day for every 400 km or 5+ hrs driving)
        - Estimated CO2 footprint (approx 0.17 kg CO2 / km for tour van)
        - Paired artist media assets for the circuit
        """
        if route_clusters is None:
            route_clusters = self.get_circuit_route(method=method, min_vibe=min_vibe)

        if not route_clusters:
            return {
                "total_distance_km": 0.0,
                "total_drive_hours": 0.0,
                "recommended_rest_days": 0,
                "est_carbon_kg": 0.0,
                "leg_details": [],
                "paired_media": []
            }

        legs = []
        total_dist = 0.0

        for i in range(len(route_clusters) - 1):
            c1 = route_clusters[i]
            c2 = route_clusters[i + 1]

            # Support both cluster objects (with 'center' dict) and individual venue objects (with 'latitude'/'longitude')
            c1_lat = c1['center']['lat'] if 'center' in c1 else (c1.get('latitude') or 0.0)
            c1_lon = c1['center']['lon'] if 'center' in c1 else (c1.get('longitude') or 0.0)
            c2_lat = c2['center']['lat'] if 'center' in c2 else (c2.get('latitude') or 0.0)
            c2_lon = c2['center']['lon'] if 'center' in c2 else (c2.get('longitude') or 0.0)

            dist = self._haversine(c1_lat, c1_lon, c2_lat, c2_lon)
            drive_hrs = round(dist / 85.0, 1)
            total_dist += dist

            c1_cities = list({v.get('city') for v in c1.get('venues', []) if v.get('city')}) if 'venues' in c1 else [c1.get('city', f"Stop {i+1}")]
            c2_cities = list({v.get('city') for v in c2.get('venues', []) if v.get('city')}) if 'venues' in c2 else [c2.get('city', f"Stop {i+2}")]
            origin_name = c1_cities[0] if c1_cities else f"Cluster {i+1}"
            dest_name = c2_cities[0] if c2_cities else f"Cluster {i+2}"

            legs.append({
                "from_cluster": i + 1,
                "to_cluster": i + 2,
                "origin": origin_name,
                "destination": dest_name,
                "distance_km": round(dist, 1),
                "drive_hours": drive_hrs
            })

        total_drive_hrs = round(total_dist / 85.0, 1)
        # Recommendation: 1 rest day for every 400 km or 5h driving
        rest_days = max(1, math.ceil(total_dist / 400.0)) if total_dist > 250 else 0
        carbon_kg = round(total_dist * 0.17, 1)

        # Contextual media matching
        identity_info = self.ai._get_identity_context(artist_id=artist_id)
        paired_media = []
        if identity_info.get("epk_link"):
            paired_media.append({"title": "Electronic Press Kit (EPK)", "url": identity_info["epk_link"]})
        if identity_info.get("mix_link"):
            paired_media.append({"title": "Headline Live Mix", "url": identity_info["mix_link"]})

        return {
            "total_distance_km": round(total_dist, 1),
            "total_drive_hours": total_drive_hrs,
            "recommended_rest_days": rest_days,
            "est_carbon_kg": carbon_kg,
            "leg_details": legs,
            "paired_media": paired_media,
            "cluster_count": len(route_clusters)
        }

    def plan_optimized_tour(self, cluster_index=None, min_vibe=6.5, artist_id=None):
        """
        Takes clusters of venues and uses AI to suggest an optimal
        visiting sequence and outreach strategy for a tour across the Midwest circuit
        and Toronto (Ontario), filtered by high-vibe threshold (6.5+) and incorporating
        the artist identity system.
        """
        if not self.ai or not self.ai.client:
            return "Tour Planning requires an active AI Engine."

        clusters = self.analytics.get_venue_clusters(min_vibe=min_vibe)
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

        # Load artist identity context
        identity_info = self.ai._get_identity_context(artist_id=artist_id)
        identity_context = identity_info.get("context", "")
        identity_note = f"\nArtist / Collective Identity:\n{identity_context}\n" if identity_context else ""

        # Check for Toronto venues in route to append cross-border customs/logistics
        has_toronto = any(
            any('toronto' in (v.get('city', '') or '').lower() or 'ontario' in (v.get('city', '') or '').lower() for v in c.get('venues', []))
            for c in route_clusters
        )
        cross_border_note = (
            "\nSpecial Logistics for Toronto / Ontario: Include cross-border travel requirements "
            "(Detroit-Windsor Ambassador Bridge or Tunnel border crossing, equipment ATA carnets / gear declarations, "
            "and CAD/USD settlement tips)."
            if has_toronto else ""
        )

        prompt = f"""
        Plan an optimal psytrance tour route for {tour_scope} based on the following venues:
        {chr(10).join(venues_summary)}
        {identity_note}
        Circuit Focus: Midwest corridor anchored in Detroit (Chicago, Ann Arbor, Grand Rapids, Cleveland, Columbus) expanding to Toronto.
        Vibe Standard: High-vibe qualification threshold (>= {min_vibe}/10).

        Provide:
        1. An optimal visiting sequence (route) that minimizes travel time between venues and clusters.
        2. A cohesive 'tour pitch' strategy emphasizing our artist branding and regional presence.
        3. Logistics advice for this specific route.{cross_border_note} {variant_advice}

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

    def generate_cluster_pitch(self, cluster_index=0, min_vibe=6.5, artist_id=None):
        """Generates a unified tour residency pitch for all venues in a cluster incorporating artist branding."""
        if not self.ai or not self.ai.client:
            return None

        clusters = self.analytics.get_venue_clusters(min_vibe=min_vibe)
        if not clusters or cluster_index >= len(clusters):
            return None

        cluster = clusters[cluster_index]
        venues_list = cluster['venues']
        venues_names = ", ".join([v['name'] for v in venues_list])

        identity_info = self.ai._get_identity_context(artist_id=artist_id)
        artist_name = identity_info.get("artist_name") or "our collective"
        epk = identity_info.get("epk_link", "")
        mix = identity_info.get("mix_link", "")
        links = []
        if epk: links.append(f"EPK: {epk}")
        if mix: links.append(f"Live Mix: {mix}")
        links_str = f" ({', '.join(links)})" if links else ""

        prompt = f"""
        Write a professional cold email proposing a psytrance 'regional residency tour' on behalf of {artist_name}{links_str}.
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
