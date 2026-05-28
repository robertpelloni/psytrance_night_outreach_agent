import json
from src.ai_engine import AIEngine
from src.db_manager import DatabaseManager
from src.analytics import AnalyticsEngine

class TourPlanner:
    def __init__(self, db_path='database/outreach.db', ai=None):
        self.ai = ai or AIEngine()
        self.db = DatabaseManager(db_path=db_path)
        self.analytics = AnalyticsEngine(db_path=db_path)

    def plan_optimized_tour(self, cluster_index=0):
        """
        Takes a cluster of venues and uses AI to suggest an optimal
        visiting sequence and outreach strategy for a tour.
        """
        if not self.ai or not self.ai.client:
            return "Tour Planning requires an active AI Engine."

        clusters = self.analytics.get_venue_clusters()
        if not clusters or cluster_index >= len(clusters):
            return "No clusters available for planning."

        cluster = clusters[cluster_index]
        venues_list = cluster['venues']

        # Format venues for AI
        venues_summary = []
        for v in venues_list:
            venues_summary.append(f"- {v['name']} ({v['vibe_score']}/10)")

        prompt = f"""
        Plan a multi-city psytrance tour for the following venues located in the same geographic region:
        {chr(10).join(venues_summary)}

        Provide:
        1. An optimal visiting sequence.
        2. A cohesive 'tour pitch' strategy that emphasizes the connection between these venues.
        3. Logistics advice for this specific cluster.

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

if __name__ == "__main__":
    planner = TourPlanner()
    print(planner.plan_optimized_tour())
