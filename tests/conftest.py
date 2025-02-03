import pytest
from flask import Flask
from unittest.mock import patch
from peewee import SqliteDatabase
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import  User, Wallet, Transaction
#from ..app import app, User, Wallet, Transaction

VALID_TOKEN = "valid_test_token"
TEST_USER_ID = 1

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_oauth():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'valid': True,
            'user_id': TEST_USER_ID
        }
        yield mock_post

@pytest.fixture
def test_db():
    test_db = SqliteDatabase(':memory:')
    with test_db.bind_ctx([User, Wallet, Transaction]):
        test_db.create_tables([User, Wallet, Transaction])
        yield test_db
        test_db.drop_tables([User, Wallet, Transaction])

@pytest.fixture
def auth_headers():
    return {'Authorization': f'Bearer {VALID_TOKEN}'}
