
import pytest

from app import app, init_db


@pytest.fixture
def client():
    init_db()  # Ensure DB is initialized
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_all_media(client):
    response = client.get('/media/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_post_and_search_media(client):
    payload = {
        "title": "Test Album",
        "artist": "Test Artist",
        "location": "Shelf A",
        "format": "CD",
    }
    post_resp = client.post('/media/', json=payload)
    assert post_resp.status_code == 201
    post_data = post_resp.get_json()
    assert 'id' in post_data

    search_resp = client.get('/media/search?query=Test')
    assert search_resp.status_code == 200
    search_results = search_resp.get_json()
    assert any(item['title'] == "Test Album" for item in search_results)


def test_delete_media(client):
    # First, add one to delete
    response = client.post('/media/', json={
        "title": "To Delete",
        "artist": "Gone Soon",
        "location": "Box X",
        "format": "Vinyl",
    })
    media_id = response.get_json()['id']

    # Now delete it
    delete_resp = client.delete(f'/media/{media_id}')
    assert delete_resp.status_code == 200
    assert "deleted" in delete_resp.get_json()['message']
