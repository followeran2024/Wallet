import json,os,sys
from decimal import Decimal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from models import  User, Wallet, Transaction
def test_create_transaction(client, mock_oauth, test_db, auth_headers):
    user = User.create(username='testuser', email='test@example.com')
    wallet = Wallet.create(user=user, currency='IRT', balance=1000)
    
    data = {
        'wallet_id': wallet.id,
        'amount': 100,
        'transaction_type': 'debit',
        'description': 'Test transaction'
    }
    
    response = client.post('/api/transactions', 
                          headers=auth_headers,
                          json=data)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['new_balance'] == 900

def test_insufficient_funds(client, mock_oauth, test_db, auth_headers):
    user = User.create(username='testuser', email='test@example.com')
    wallet = Wallet.create(user=user, currency='IRT', balance=50)
    
    data = {
        'wallet_id': wallet.id,
        'amount': 100,
        'transaction_type': 'debit'
    }
    
    response = client.post('/api/transactions', 
                          headers=auth_headers,
                          json=data)
    assert response.status_code == 400
    assert b'Insufficient funds' in response.data

def test_get_transactions(client, mock_oauth, test_db, auth_headers):
    user = User.create(username='testuser', email='test@example.com')
    wallet = Wallet.create(user=user, currency='IRT')
    Transaction.create(wallet=wallet, amount=100, transaction_type='credit')
    
    response = client.get('/api/transactions', headers=auth_headers)
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert len(response_data['transactions']) == 1
