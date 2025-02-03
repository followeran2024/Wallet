import json,os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from models import  User, Wallet, Transaction
def test_create_user_success(client, mock_oauth, test_db, auth_headers):
    data = {
        'username': 'testuser',
        'email': 'test@example.com'
    }
    response = client.post('/api/users', 
                          headers=auth_headers,
                          json=data)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['user']['username'] == 'testuser'

def test_create_duplicate_user(client, mock_oauth, test_db, auth_headers):
    data = {
        'username': 'testuser',
        'email': 'test@example.com'
    }
    client.post('/api/users', headers=auth_headers, json=data)
    response = client.post('/api/users', headers=auth_headers, json=data)
    assert response.status_code == 400
    assert b'Username or email already exists' in response.data
