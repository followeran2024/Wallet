from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
import time,os
from models import *
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

admin_api = Blueprint('admin', __name__)

# Configure rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per minute"]
)

ADMIN_TOKEN=os.getenv('ADMIN_TOKEN')


def require_admin_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Admin-Token')
        if not token or token != ADMIN_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_api.route('/wallet', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
@require_admin_token
def get_wallet_admin():
    if request.method == 'GET':
        try:
            wallets = Wallet.select()
            return jsonify([wallet.serialize() for wallet in wallets]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            required_fields = ['user_id', 'currency']
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400

            user = User.get_by_id(data['user_id'])
            wallet = Wallet.create(
                user=user,
                currency=data['currency'],
                balance=data.get('balance', 0),
                is_active=data.get('is_active', True)
            )
            return jsonify(wallet.serialize()), 201
        except User.DoesNotExist:
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@admin_api.route('/user', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
@require_admin_token
def get_user_admin():
    if request.method == 'GET':
        try:
            users = User.select()
            return jsonify([{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            } for user in users]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data.get('username'):
                return jsonify({"error": "Username is required"}), 400

            user = User.create(
                username=data['username'],
                email=data.get('email')
            )
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@admin_api.route('/transaction', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
@require_admin_token
def get_transaction_admin():
    if request.method == 'GET':
        try:
            transactions = Transaction.select()
            return jsonify([{
                'id': tx.id,
                'wallet_id': tx.wallet.id,
                'amount': float(tx.amount),
                'transaction_type': tx.transaction_type,
                'description': tx.description,
                'status': tx.status,
                'created_at': tx.created_at.isoformat()
            } for tx in transactions]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            required_fields = ['wallet_id', 'amount', 'transaction_type']
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400

            wallet = Wallet.get_by_id(data['wallet_id'])
            transaction = Transaction.create(
                wallet=wallet,
                amount=data['amount'],
                transaction_type=data['transaction_type'],
                description=data.get('description'),
                status=data.get('status', 'pending')
            )
            from decimal import Decimal
            if data['transaction_type'] == 'credit':
                wallet.balance += Decimal(str(data['amount']))
            else:
                wallet.balance -= Decimal(str(data['amount']))
        
            return jsonify({
                'id': transaction.id,
                'wallet_id': transaction.wallet.id,
                'amount': float(transaction.amount),
                'transaction_type': transaction.transaction_type,
                'description': transaction.description,
                'status': transaction.status,
                'created_at': transaction.created_at.isoformat()
            }), 201
        except Wallet.DoesNotExist:
            return jsonify({"error": "Wallet not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Delete routes
@admin_api.route('/wallet/<int:wallet_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
@require_admin_token
def delete_wallet(wallet_id):
    try:
        wallet = Wallet.get_by_id(wallet_id)
        wallet.delete_instance()
        return jsonify({"message": "Wallet deleted successfully"}), 200
    except Wallet.DoesNotExist:
        return jsonify({"error": "Wallet not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_api.route('/user/<int:user_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
@require_admin_token
def delete_user(user_id):
    try:
        user = User.get_by_id(user_id)
        user.delete_instance()
        return jsonify({"message": "User deleted successfully"}), 200
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_api.route('/transaction/<int:transaction_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
@require_admin_token
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.get_by_id(transaction_id)
        transaction.delete_instance()
        return jsonify({"message": "Transaction deleted successfully"}), 200
    except Transaction.DoesNotExist:
        return jsonify({"error": "Transaction not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500