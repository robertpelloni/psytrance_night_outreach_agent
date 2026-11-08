import json
import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Collaborative filtering and alternate venue recommendation engine.
    Analyzes acoustic profiles, musical traits, geographic proximity,
    and historical pipeline outcomes to suggest high-affinity alternative venues.
    """

    def __init__(self, db_manager):
        self.db = db_manager

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance in kilometers between two points."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @staticmethod
    def _extract_trait_set(venue: Dict[str, Any]) -> set:
        """Extract a normalized set of traits, tags, and acoustic markers from venue dict."""
        traits = set()

        # Parse extracted_traits (JSON string, dict, or list)
        raw_traits = venue.get("extracted_traits")
        if raw_traits:
            if isinstance(raw_traits, str):
                try:
                    parsed = json.loads(raw_traits)
                except Exception:
                    parsed = [t.strip().lower() for t in raw_traits.split(",") if t.strip()]
            else:
                parsed = raw_traits

            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    if isinstance(v, list):
                        for item in v:
                            traits.add(str(item).strip().lower())
                    elif isinstance(v, bool) and v:
                        traits.add(str(k).strip().lower())
                    elif v:
                        traits.add(f"{k}:{v}".strip().lower())
            elif isinstance(parsed, list):
                for item in parsed:
                    traits.add(str(item).strip().lower())

        # Parse tags
        raw_tags = venue.get("tags")
        if raw_tags:
            if isinstance(raw_tags, str):
                for tag in raw_tags.split(","):
                    tag_clean = tag.strip().lower()
                    if tag_clean:
                        traits.add(tag_clean)
            elif isinstance(raw_tags, list):
                for tag in raw_tags:
                    traits.add(str(tag).strip().lower())

        # Include venue_type if present
        venue_type = venue.get("venue_type")
        if venue_type:
            traits.add(str(venue_type).strip().lower())

        return traits

    def get_recommendations(
        self,
        target_venue_id: str,
        limit: int = 5,
        min_score: float = 0.15,
        exclude_rejected: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Calculates similarity between target venue and all eligible venues.
        Returns top alternatives sorted by composite affinity score.
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Fetch target venue details
        cursor.execute("""
            SELECT v.*, l.pipeline_status, l.vibe_score, l.id as lead_id
            FROM venues v
            LEFT JOIN outreach_leads l ON v.id = l.venue_id
            WHERE v.id = ?
        """, (target_venue_id,))
        target_row = cursor.fetchone()

        if not target_row:
            logger.warning(f"Target venue {target_venue_id} not found.")
            return []

        col_names = [d[0] for d in cursor.description]
        target = dict(zip(col_names, target_row))
        target_traits = self._extract_trait_set(target)

        # Fetch candidate venues
        query = """
            SELECT v.*, l.pipeline_status, l.vibe_score, l.id as lead_id
            FROM venues v
            LEFT JOIN outreach_leads l ON v.id = l.venue_id
            WHERE v.id != ?
        """
        params = [target_venue_id]
        if exclude_rejected:
            query += " AND (l.pipeline_status IS NULL OR l.pipeline_status NOT IN ('REJECTED', 'LOST'))"

        cursor.execute(query, params)
        candidate_rows = cursor.fetchall()

        recommendations = []
        target_lat = target.get("latitude")
        target_lon = target.get("longitude")

        for row in candidate_rows:
            cand = dict(zip(col_names, row))
            cand_traits = self._extract_trait_set(cand)

            # 1. Trait Jaccard Similarity (Acoustic / vibe / genre / gear)
            union = target_traits | cand_traits
            intersection = target_traits & cand_traits
            trait_sim = len(intersection) / len(union) if union else 0.0

            # 2. Geographic Proximity Score
            cand_lat = cand.get("latitude")
            cand_lon = cand.get("longitude")
            distance_km = None
            geo_score = 0.5 # default moderate proximity

            if target_lat is not None and target_lon is not None and cand_lat is not None and cand_lon is not None:
                try:
                    distance_km = round(self._haversine(float(target_lat), float(target_lon), float(cand_lat), float(cand_lon)), 1)
                    # Exponential decay over 500km circuit radius
                    geo_score = math.exp(-distance_km / 250.0)
                except Exception:
                    distance_km = None
            elif target.get("city") and cand.get("city") and target.get("city").lower() == cand.get("city").lower():
                geo_score = 0.95
                distance_km = 0.0

            # 3. Capacity & Type Compatibility
            type_score = 1.0 if target.get("venue_type") and target.get("venue_type") == cand.get("venue_type") else 0.4

            # Capacity score
            t_cap = target.get("capacity") or 300
            c_cap = cand.get("capacity") or 300
            cap_ratio = min(t_cap, c_cap) / max(t_cap, c_cap) if max(t_cap, c_cap) > 0 else 0.5

            # 4. Acoustic Profile Bonus (Premium underground sound systems)
            acoustic_systems = ["funktion-one", "void acoustics", "danley", "d&b audiotechnik", "pk sound"]
            shared_sound = any(sys in cand_traits and sys in target_traits for sys in acoustic_systems)
            sound_bonus = 0.10 if shared_sound else (0.05 if any(sys in cand_traits for sys in acoustic_systems) else 0.0)

            # 5. Lead Vibe / Conversion Quality Bonus
            vibe_score = cand.get("vibe_score") or 0.0
            vibe_bonus = min(float(vibe_score) / 10.0, 1.0) * 0.15

            # Composite Affinity Calculation (0.0 to 1.0 scale)
            composite_score = (
                (trait_sim * 0.35) +
                (geo_score * 0.25) +
                (type_score * 0.15) +
                (cap_ratio * 0.10) +
                sound_bonus +
                vibe_bonus
            )
            composite_score = round(min(composite_score, 1.0), 3)

            if composite_score >= min_score:
                reasoning = []
                if intersection:
                    common_items = list(intersection)[:4]
                    reasoning.append(f"Shared traits: {', '.join(common_items)}")
                if distance_km is not None:
                    if distance_km <= 50:
                        reasoning.append(f"Within local cluster ({distance_km} km)")
                    else:
                        reasoning.append(f"Transit corridor distance: {distance_km} km")
                if target.get("city") == cand.get("city"):
                    reasoning.append(f"Same market ({cand.get('city')})")
                if cand.get("vibe_score"):
                    reasoning.append(f"Vibe score: {cand.get('vibe_score')}/10")

                recommendations.append({
                    "venue_id": cand.get("id"),
                    "name": cand.get("name"),
                    "city": cand.get("city"),
                    "venue_type": cand.get("venue_type"),
                    "capacity": cand.get("capacity"),
                    "vibe_score": cand.get("vibe_score"),
                    "pipeline_status": cand.get("pipeline_status") or "NEW",
                    "lead_id": cand.get("lead_id"),
                    "distance_km": distance_km,
                    "match_score": composite_score,
                    "shared_traits": list(intersection),
                    "reasoning": " | ".join(reasoning) if reasoning else "Compatible market profile"
                })

        # Rank by match score descending
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:limit]

    def generate_contingency_pitch(
        self,
        target_venue_id: str,
        alt_venue_id: str,
        ai_engine=None,
        artist_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generates a tailored outreach email pitching the alternative sibling venue
        when a primary prospect has stalled, rejected, or presents a scheduling conflict.
        Incorporates collective branding and acoustic alignment.
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM venues WHERE id = ?", (target_venue_id,))
        target = cursor.fetchone()
        cursor.execute("SELECT * FROM venues WHERE id = ?", (alt_venue_id,))
        alt = cursor.fetchone()

        if not target or not alt:
            return {"status": "error", "message": "Target or alternate venue not found"}

        col_names = [d[0] for d in cursor.description]
        target_dict = dict(zip(col_names, target))
        alt_dict = dict(zip(col_names, alt))

        # Acoustic traits
        alt_traits = list(self._extract_trait_set(alt_dict))[:5]
        target_name = target_dict.get("name", "our circuit target")
        alt_name = alt_dict.get("name")
        alt_city = alt_dict.get("city", "Detroit")

        identity_info = ai_engine._get_identity_context(artist_id=artist_id) if ai_engine else {}
        artist_name = identity_info.get("artist_name") or "our collective"
        epk = identity_info.get("epk_link", "")
        mix = identity_info.get("mix_link", "")

        prompt = f"""
        Write a professional, highly targeted cold outreach email pitching a psytrance night residency at {alt_name} ({alt_city}).
        Context: We are actively routing our regional Midwest tour (anchored in Detroit). While coordinating circuit dates near {target_name},
        we identified {alt_name} as the premier acoustic match for our sound.

        Venue Details:
        - Venue: {alt_name}
        - Market: {alt_city}
        - Notable traits: {', '.join(alt_traits)}
        - Artist/Collective: {artist_name}
        {f"- EPK: {epk}" if epk else ""}
        {f"- Live Mix: {mix}" if mix else ""}

        Philosophy:
        - Selector, Not Promoter: Focus on artistic curation, acoustic immersion, and scene building.
        - Tone: Underground, respectful, low friction, proposing a turnkey psytrance club night.

        Return a JSON object with:
        {{
            "subject": "...",
            "body": "..."
        }}
        """

        if ai_engine and ai_engine.client:
            try:
                resp = ai_engine.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                parsed = json.loads(resp.choices[0].message.content)
                return {
                    "status": "success",
                    "target_venue": target_name,
                    "alt_venue": alt_name,
                    "subject": parsed.get("subject"),
                    "pitch": parsed.get("body")
                }
            except Exception as e:
                logger.error(f"Error generating contingency pitch via AI: {e}")

        # Fallback template
        subject = f"Psytrance Night Residency Proposal - {alt_name} / {alt_city}"
        body = (
            f"Hi {alt_name} team,\n\n"
            f"We are coordinating regional Midwest circuit dates for {artist_name} and wanted to connect with your team directly. "
            f"Given your outstanding acoustic reputation and underground aesthetic in {alt_city}, your space is an ideal fit "
            f"for a curated psytrance night.\n\n"
            f"We handle turnkey production, decor, and regional underground promotion.\n\n"
            f"{f'Press Kit: {epk}' if epk else ''}\n"
            f"{f'Recent Mix: {mix}' if mix else ''}\n\n"
            f"Would you be open to exploring a trial residency date next month?\n\n"
            f"Best regards,\n{artist_name}"
        )
        return {
            "status": "success",
            "target_venue": target_name,
            "alt_venue": alt_name,
            "subject": subject,
            "pitch": body
        }
