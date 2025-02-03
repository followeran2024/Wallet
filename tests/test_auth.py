import pytest,sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_missing_token(client):
    response = client.post('/api/users')
    assert response.status_code == 401
    assert b'Bearer token is required' in response.data

def test_invalid_token(client, mock_oauth):
    mock_oauth.return_value.json.return_value = {'valid': False}
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.post('/api/users', headers=headers)
    assert response.status_code == 401
    assert b'Invalid token' in response.data

