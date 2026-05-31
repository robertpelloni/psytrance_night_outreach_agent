import sqlite3
import json
import os
from .ai_engine import AIEngine

class OutreachPredictor:
    """Predicts the likelihood of outreach success based on venue traits and historical sentiment."""

    def __init__(self, db_path='database/outreach.db'):
        self.db_path = db_path
        self.ai = AIEngine()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def predict_success_probability(self, lead_id, use_cache=True):
        """
        Calculates a success probability (0-100%) for a given lead.
        Uses a combination of historical success rates and AI-driven trait analysis.
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row

            if use_cache:
                cached = conn.execute("SELECT success_probability FROM outreach_leads WHERE id = ?", (lead_id,)).fetchone()
                if cached and cached['success_probability'] is not None:
                    return cached['success_probability']

            # Fetch lead and venue details
            query = """
            SELECT l.vibe_score, v.extracted_traits, v.city
            FROM outreach_leads l
            JOIN venues v ON l.venue_id = v.id
            WHERE l.id = ?
            """
            lead = conn.execute(query, (lead_id,)).fetchone()
            if not lead:
                return 0

            # 1. Base Probability from Vibe Score (Heuristic)
            # Vibe score is 1-10, so base prob is vibe_score * 8 (e.g. 8/10 -> 64%)
            probability = (lead['vibe_score'] or 0) * 8

            # 2. Historical City Success Rate (Empirical)
            city_stats = conn.execute("""
                SELECT
                    SUM(CASE WHEN r.sentiment = 'INTERESTED' THEN 1 ELSE 0 END) as interested,
                    COUNT(r.id) as total
                FROM lead_replies r
                JOIN outreach_leads l ON r.lead_id = l.id
                JOIN venues v ON l.venue_id = v.id
                WHERE v.city = ?
            """, (lead['city'],)).fetchone()

            if city_stats and city_stats['total'] > 0:
                city_success_rate = (city_stats['interested'] / city_stats['total']) * 100
                # Blend in city rate (30% weight)
                probability = (probability * 0.7) + (city_success_rate * 0.3)

            # 3. AI Trait Alignment (Contextual)
            traits = lead['extracted_traits']
            if traits and self.ai.client:
                # Ask AI to adjust probability based on technical traits
                traits_json = json.loads(traits)
                adjustment = self._get_ai_adjustment(traits_json)
                probability += adjustment

            # Clamp between 0 and 95 (nothing is 100% certain)
            prob = max(5, min(95, round(probability, 1)))

            # Persist to cache
            conn.execute("UPDATE outreach_leads SET success_probability = ? WHERE id = ?", (prob, lead_id))
            conn.commit()

            return prob

    def _get_ai_adjustment(self, traits):
        """Uses AI to provide a +/- adjustment to the success probability."""
        prompt = f"""
        Given the following venue traits, how suitable are they for a psytrance night?
        {json.dumps(traits)}

        If they have Funktion-One/Void sound, projection mapping, or an 'underground' atmosphere, return a positive integer (up to 15).
        If they seem too commercial or have conflicting music policies, return a negative integer (down to -15).
        Otherwise, return 0.

        Output ONLY the integer.
        """
        try:
            response = self.ai.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return int(response.choices[0].message.content.strip())
        except:
            return 0
