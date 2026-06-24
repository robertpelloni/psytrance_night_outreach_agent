import pytest
from src.dashboard.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_add_venue_manually(client, monkeypatch):
    import main

    called = []
    def mock_qualify(*args, **kwargs):
        called.append(args[0]['name'])

    monkeypatch.setattr(main, 'qualify_and_pitch', mock_qualify)

    response = client.post('/add_venue_manually', data={
        'name': 'Test Manual Venue',
        'city': 'Detroit',
        'website': 'https://test.com',
        'notes': 'Cool vibe'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Check that thread was spawned and it called mock_qualify
    import time
    time.sleep(0.5) # give thread time to execute

    assert 'Test Manual Venue' in called

def test_add_venue_manually_missing_data(client):
    response = client.post('/add_venue_manually', data={
        'name': '',
        'city': 'Detroit'
    })

    assert response.status_code == 400
    assert b"Name and City are required" in response.data
