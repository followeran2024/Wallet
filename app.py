from flask import Flask, request, jsonify,render_template
from models import *
from datetime import datetime, timezone
from playhouse.shortcuts import model_to_dict
import decimal
import requests,logging
from functools import wraps
from peewee import IntegrityError, DoesNotExist
from dotenv import load_dotenv
from flask_cors import CORS
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
#initialize_db()
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Configuration
OAUTH_SERVICE_URL = os.getenv('VALIDATE_TOKEN_URL')
# Decorator for OAuth2 protection
def require_oauth2_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log the start of the OAuth2 token validation
        logger.info(f"Validating OAuth2 token for endpoint: {request.endpoint}")

        # Get the token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Bearer token is missing or invalid")
            return jsonify({'error': 'Bearer token is required'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Validate token with the OAuth service
        try:
            logger.info(f"Sending token validation request to OAuth service: {OAUTH_SERVICE_URL}")
            response = requests.post(
                OAUTH_SERVICE_URL,
                json={'token': token},
                headers={'Content-Type': 'application/json'}
            )
            
            validation_result = response.json()
            
            if response.status_code != 200 or not validation_result.get('valid'):
                logger.warning(f"Token validation failed: {validation_result.get('message', 'Token validation failed')}")
                return jsonify({
                    'error': 'Invalid token',
                    'message': validation_result.get('message', 'Token validation failed')
                }), 401
            
            # Add user_id to request context for use in the protected endpoint
            request.user_id = validation_result.get('username')
            logger.info(f"Token validated successfully for user_id: {request.user_id}")
            
            return f(*args, **kwargs)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OAuth service unavailable: {str(e)}")
            return jsonify({
                'error': 'Authentication service unavailable',
                'message': str(e)
            }), 503
    
    return decorated_function


# Protected endpoints with OAuth2
@app.route('/api/users', methods=['POST'])
@require_oauth2_token
def create_user():
    db.connect(True)
    logger.info("Creating a new user")
    data = request.get_json()
    try:
        user = User.create(
            username=data['username'],
            email=data['email']
        )
        logger.info(f"User created successfully: {user.id}")
        wallet = Wallet.create(
            user=user,
            currency=data.get('currency', 'IRT')
        )
        logger.info(f"created {wallet.id} wallet for user {user.id}")
        return jsonify({'message': 'User created successfully', 'user': model_to_dict(user),'wallet_id':wallet.id}), 201# returning handled wallet
    except IntegrityError:
        logger.error("Username or email already exists")
        return jsonify({'error': 'Username or email already exists'}), 400

@app.route('/api/wallets', methods=['POST','GET'])
@require_oauth2_token
def create_wallet():
    db.connect(True)
    if str(request.method).lower()=="get":# creating wallet is handled on /api/users while user creation
        return [x.serialize() for x in Wallet.select()] 
    logger.info("Creating a new wallet")
    data = request.get_json()
    try:
        # Use the user_id from the validated token
        user = User.get_by_id(request.user_id)
        wallet = Wallet.create(
            user=user,
            currency=data.get('currency', 'IRT')
        )
        logger.info(f"Wallet created successfully: {wallet.id}")
        return jsonify({'message': 'Wallet created successfully', 'wallet': model_to_dict(wallet)}), 201
    except User.DoesNotExist:
        logger.error(f"User not found: {request.user_id}")
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/wallets/<int:wallet_id>', methods=['GET'])
@require_oauth2_token
def get_wallet(wallet_id):
    db.connect(True)
    logger.info(f"Fetching wallet with ID: {wallet_id}")
    try:
        # Add user verification to ensure users can only access their own wallets
        wallet = Wallet.get(
            (Wallet.id == wallet_id) & 
            (Wallet.user_id == request.user_id)
        )
        logger.info(f"Wallet retrieved successfully: {wallet.id}")
        return jsonify(model_to_dict(wallet))
    except Wallet.DoesNotExist:
        logger.error(f"Wallet not found: {wallet_id}")
        return jsonify({'error': 'Wallet not found'}), 404

@app.route('/api/transactions', methods=['POST'])
@require_oauth2_token
def create_transaction():
    db.connect(True)
    logger.info("Creating a new transaction")
    data = request.get_json()
    try:
        owner=User.get_or_none(User.username==data['user_id'])

        wallet = Wallet.get(
            (Wallet.id == data['wallet_id']) & 
            (Wallet.user == owner)
        )
        logger.warning(f"user {owner.username} requested for access to wallet {wallet.id}")
        if owner is None or wallet.user!=owner:
            return jsonify({'error': 'Invalid input data OR Wrong credential for the wallet'}), 400
        if not wallet.is_active:
            logger.warning(f"Wallet is inactive: {wallet.id}")
            return jsonify({'error': 'Wallet is inactive'}), 400

        amount = decimal.Decimal(str(data['amount']))
        
        if data['transaction_type'] == 'debit' and wallet.balance < amount:
            logger.warning(f"Insufficient funds in wallet: {wallet.id}")
            return jsonify({'error': 'Insufficient funds'}), 400

        transaction = Transaction.create(
            wallet=wallet,
            amount=amount,
            transaction_type=data['transaction_type'],
            description=data.get('description', ''),
            status='completed'
        )

        if data['transaction_type'] == 'credit':
            wallet.balance += amount
        else:
            wallet.balance -= amount
        
        wallet.updated_at = datetime.now()
        wallet.save()

        logger.info(f"Transaction completed successfully: {transaction.id}")
        return jsonify({
            'message': 'Transaction completed successfully',
            'transaction': model_to_dict(transaction),
            'new_balance': float(wallet.balance)
        }), 201

    except Wallet.DoesNotExist:
        logger.error(f"Wallet not found or unauthorized access: {data.get('wallet_id')}")
        return jsonify({'error': 'Wallet not found or unauthorized access'}), 404
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid input data: {str(e)}")
        return jsonify({'error': 'Invalid input data'}), 400

@app.route('/api/transactions', methods=['GET'])
@require_oauth2_token
def get_transactions():
    db.connect(True)
    logger.info("Fetching transactions")
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    wallet_id = request.args.get('wallet_id')
    owner= User.get_or_none(User.username==request.user_id)
    if not owner:
        return {'error':f'User / Wallet owner not found {str(request.user_id)}'},404
    query = (Transaction
             .select()
             .join(Wallet)
             .where(Wallet.user == owner.id))
    
    if wallet_id:
        query = query.where(Transaction.wallet_id == wallet_id)
    
    total_count = query.count()
    
    transactions = (query
                   .order_by(Transaction.created_at.desc())
                   .paginate(page, per_page))
    
    logger.info(f"Retrieved {len(transactions)} transactions")
    return jsonify({
        'transactions': [model_to_dict(t) for t in transactions],
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page
    })


#if __name__ == '__main__':
#    app.run(debug=True)