import json,os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from models import  User, Wallet
def test_create_wallet(client, mock_oauth, test_db, auth_headers):
    # Create test user first
    user = User.create(username='testuser', email='test@example.com')
    
    data = {'currency': 'USD'}
    response = client.post('/api/wallets', 
                          headers=auth_headers,
                          json=data)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['wallet']['currency'] == 'USD'

def test_get_wallet(client, mock_oauth, test_db, auth_headers):
    user = User.create(username='testuser', email='test@example.com')
    wallet = Wallet.create(user=user, currency='IRT')
    
    response = client.get(f'/api/wallets/{wallet.id}', 
                         headers=auth_headers)
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['currency'] == 'IRT'

def test_get_nonexistent_wallet(client, mock_oauth, test_db, auth_headers):
    response = client.get('/api/wallets/999', headers=auth_headers)
    assert response.status_code == 404
