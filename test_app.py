# test_app.py - Integration tests for Don's Media Archive API.
"""
Integration tests for Don's Media Archive API.

This module uses pytest fixtures and Flask's test client to verify the behavior of
the media archive endpoints, ensuring each test runs against a fresh database.

Endpoints tested:
- GET /media/
- POST /media/
- GET /media/search?query=...
- DELETE /media/<media_id>
"""

import pytest

from app import app, init_db


@pytest.fixture
def client():
    """
    Create and configure a new Flask test client for each test.

    Initializes a fresh SQLite database and enables testing mode on the app,
    then yields a test client to perform HTTP requests.
    """
    # Initialize the test database schema
    init_db()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_all_media(client):
    """
    Test that the GET /media/ endpoint returns a 200 status code
    and that the response body is a list (even if empty).
    """
    response = client.get('/media/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_post_and_search_media(client):
    """
    Test creating a new media entry via POST /media/ and then
    retrieving it using GET /media/search?query=<title>.

    Verifies that:
    - POST returns 201 and an 'id' in the response
    - SEARCH returns a list containing the newly created item
    """
    payload = {
        "title": "Test Album",
        "artist": "Test Artist",
        "location": "Shelf A",
        "format": "CD",
    }
    # Create a new media entry
    post_resp = client.post('/media/', json=payload)
    assert post_resp.status_code == 201
    post_data = post_resp.get_json()
    assert 'id' in post_data

    # Search for the created entry
    search_resp = client.get('/media/search?query=Test')
    assert search_resp.status_code == 200
    search_results = search_resp.get_json()
    assert any(item['title'] == "Test Album" for item in search_results)


def test_delete_media(client):
    """
    Test deleting a media entry via DELETE /media/<media_id>.

    Verifies that:
    - POST creates a new entry
    - DELETE returns 200 and a success message
    """
    # Create an entry to delete
    response = client.post('/media/', json={
        "title": "To Delete",
        "artist": "Gone Soon",
        "location": "Shelf X",
        "format": "Vinyl",
    })
    media_id = response.get_json()['id']

    # Delete the entry
    delete_resp = client.delete(f'/media/{media_id}')
    assert delete_resp.status_code == 200
    assert "deleted" in delete_resp.get_json()['message']

