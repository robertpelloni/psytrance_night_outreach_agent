import unittest
import os
import shutil
import tempfile
from src.analytics import AnalyticsEngine
from src.db_manager import DatabaseManager
from src.tour_planner import TourPlanner
from unittest.mock import patch, MagicMock

class TestTourAnalytics(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_tour.db")
        self.db = DatabaseManager(db_path=self.db_path)
        self.analytics = AnalyticsEngine(db_path=self.db_path)
        self.planner = TourPlanner(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_venue_clustering_logic(self):
        """Verify that venues within range are correctly clustered."""
        # 1. Add two venues in Berlin (very close)
        self.db.add_venue({'id': 'v1', 'name': 'Berghain', 'city': 'Berlin', 'latitude': 52.5112, 'longitude': 13.4431})
        self.db.add_venue({'id': 'v2', 'name': 'Watergate', 'city': 'Berlin', 'latitude': 52.501, 'longitude': 13.44})

        # 2. Add one venue in London (far away)
        self.db.add_venue({'id': 'v3', 'name': 'Fabric', 'city': 'London', 'latitude': 51.5196, 'longitude': -0.1024})

        # 3. Add leads for them
        self.db.add_lead({'venue_id': 'v1', 'vibe_score': 10})
        self.db.add_lead({'venue_id': 'v2', 'vibe_score': 9})
        self.db.add_lead({'venue_id': 'v3', 'vibe_score': 8})

        clusters = self.analytics.get_venue_clusters(radius_km=10)

        # Berlin cluster should be found (v1, v2)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]['venue_count'], 2)
        self.assertIn('Berghain', [v['name'] for v in clusters[0]['venues']])

    def test_tour_planning_interface(self):
        """Verify that the tour planner calls AI with the correct context."""
        # Setup mock AI
        mock_ai = MagicMock()
        mock_client = MagicMock()
        mock_ai.client = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="AI Tour Plan"))]
        )

        # Initialize planner with mock AI
        self.planner = TourPlanner(db_path=self.db_path, ai=mock_ai)

        # Add venues to create a cluster
        self.db.add_venue({'id': 'v1', 'name': 'V1', 'city': 'C1', 'latitude': 50.0, 'longitude': 10.0})
        self.db.add_venue({'id': 'v2', 'name': 'V2', 'city': 'C1', 'latitude': 50.1, 'longitude': 10.1})
        self.db.add_lead({'venue_id': 'v1', 'vibe_score': 10})
        self.db.add_lead({'venue_id': 'v2', 'vibe_score': 10})

        plan = self.planner.plan_optimized_tour(cluster_index=0)
        self.assertEqual(plan, "AI Tour Plan")
        self.assertTrue(mock_client.chat.completions.create.called)

if __name__ == "__main__":
    unittest.main()
