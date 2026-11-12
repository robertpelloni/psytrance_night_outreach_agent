import unittest
import os
import json
from unittest.mock import patch, MagicMock
from src.dashboard.app import app
import src.dashboard.tray as tray

class TestUnifiedDashboard(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_unified_dashboard_root(self):
        """Verify the unified root dashboard renders successfully with master tabs."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Psytrance Night Outreach", html)
        self.assertIn("masterTabs", html)
        self.assertIn("Outreach Pipeline & Queues", html)
        self.assertIn("Geographic Map & Tour Routing", html)
        self.assertIn("Analytics & A/B Testing", html)
        self.assertIn("Settings & Collective Profiles", html)
        self.assertIn("System Health & Sync Protocol", html)
        self.assertIn("Scraper Sources", html)

    def test_tab_parameters(self):
        """Verify navigation query parameters open corresponding views."""
        for tab in ['pipeline', 'map', 'analytics', 'settings', 'system', 'sources']:
            response = self.app.get(f'/?tab={tab}')
            self.assertEqual(response.status_code, 200)

    def test_legacy_routes_render_unified_dashboard(self):
        """Verify legacy routes remain compatible and render without errors."""
        routes = ['/map', '/analytics', '/settings', '/system', '/sources', '/dm_queue', '/pending_follow_ups', '/history', '/booked', '/pending_qualification']
        for route in routes:
            response = self.app.get(route)
            self.assertEqual(response.status_code, 200)

    def test_modals_rendered_in_command_center(self):
        """Verify all interactive command center modals are present in the DOM."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Onboarding Tour Modal
        self.assertIn('id="onboardingTourModal"', html)
        self.assertIn('id="tour-step-badge"', html)

        # Feedback Modal
        self.assertIn('id="feedbackModal"', html)
        self.assertIn('id="feedback-form"', html)
        self.assertIn('id="fb-category"', html)

        # Venue Comparison Modal
        self.assertIn('id="compareModal"', html)
        self.assertIn('id="compare-table"', html)

        # Pipeline Activity Digest Modal
        self.assertIn('id="digestModal"', html)
        self.assertIn('id="digest-preview-frame"', html)

        # Alternate Venues Collaborative Recommendations Modal
        self.assertIn('id="recModal"', html)
        self.assertIn('id="rec-results-container"', html)

        # Manual Venue Addition Modal
        self.assertIn('id="addVenueModal"', html)

    def test_operator_feedback_triage_rendering(self):
        """Verify the Operator Feedback table and triage elements render in the System tab."""
        response = self.app.get('/?tab=system')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Operator Feedback & Community Requests", html)
        self.assertIn("Triage Action", html)
        self.assertIn("updateFeedbackStatus", html)

    def test_geocoding_and_clustering_ui_elements(self):
        """Verify geocoding missing triggers and Map UI elements are in Map tab."""
        response = self.app.get('/?tab=map')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Geocode Missing", html)
        self.assertIn("geocodeUnlocatedVenues", html)
        self.assertIn("Plan Midwest Circuit", html)

    def test_analytics_and_engagement_strip_rendering(self):
        """Verify email engagement KPI strip and activity digest triggers in Analytics tab."""
        response = self.app.get('/?tab=analytics')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Email Engagement & Interaction Metrics", html)
        self.assertIn("Open Rate", html)
        self.assertIn("Click-Through Rate", html)
        self.assertIn("Email Pipeline Digest", html)

    def test_tray_command_execution(self):
        """Test tray companion command execution routines."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            self.assertTrue(tray.check_server_status())

        with patch('src.dashboard.tray.open_dashboard') as mock_open:
            tray.handle_single_command('1')
            mock_open.assert_called_once()

        with patch('src.dashboard.tray.run_pipeline') as mock_run:
            tray.handle_single_command('2')
            mock_run.assert_called_once()

        with patch('src.dashboard.tray.fetch_replies') as mock_fetch:
            tray.handle_single_command('3')
            mock_fetch.assert_called_once()

        with patch('src.dashboard.tray.run_sync') as mock_sync:
            tray.handle_single_command('4')
            mock_sync.assert_called_once()

    def test_shutdown_endpoint(self):
        """Test the /shutdown endpoint returns success."""
        response = self.app.post('/shutdown')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

if __name__ == "__main__":
    unittest.main()
