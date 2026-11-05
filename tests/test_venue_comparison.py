import unittest
import json
from unittest.mock import patch, MagicMock
from src.dashboard.app import app

class TestVenueComparison(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_compare_venues_missing_ids(self):
        """Ensure endpoint rejects requests without venue IDs."""
        res = self.client.post('/compare_venues', json={})
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("error", data)

    @patch('src.dashboard.app.db')
    def test_compare_venues_success(self, mock_db):
        """Ensure endpoint retrieves and formats venue comparative metadata correctly."""
        mock_db.get_venue.side_effect = lambda vid: {
            'id': vid,
            'name': f'Venue {vid}',
            'city': 'Detroit',
            'website': f'https://{vid}.com',
            'google_rating': 4.7,
            'venue_type': 'Club',
            'capacity': 400,
            'neighborhood': 'Downtown',
            'extracted_traits': json.dumps({'sound_system': 'Funktion-One', 'lighting': 'Lasers'})
        } if vid in ['v1', 'v2'] else None

        mock_db.get_lead_by_venue_id.side_effect = lambda vid: {
            'vibe_score': 9,
            'pipeline_status': 'PENDING_REVIEW',
            'success_probability': 85.0
        } if vid == 'v1' else {
            'vibe_score': 7,
            'pipeline_status': 'APPROVED',
            'success_probability': 60.0
        }

        res = self.client.post('/compare_venues', json={
            'venue_ids': ['v1', 'v2']
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('venues', data)
        self.assertEqual(len(data['venues']), 2)

        v1 = data['venues'][0]
        self.assertEqual(v1['name'], 'Venue v1')
        self.assertEqual(v1['vibe_score'], 9)
        self.assertEqual(v1['traits'].get('sound_system'), 'Funktion-One')

if __name__ == '__main__':
    unittest.main()
