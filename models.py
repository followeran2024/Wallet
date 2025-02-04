from peewee import *
from datetime import datetime, timezone
from playhouse.pool import PooledMySQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()

db = SqliteDatabase('wallet.db')

# Database configuration

# Models remain the same as before
class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)

class Wallet(BaseModel):
    user = ForeignKeyField(User, backref='wallets')
    balance = DecimalField(decimal_places=2, default=0)
    currency = CharField(default='IRT')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    def serialize(self):
        
        #db.connect(reuse_if_open=True)
        """
        Serialize the Wallet instance into a dictionary format suitable for JSON output.
        """
        return {
            'id': self.id,
            'user_id': self.user.id,
            'balance': float(self.balance),
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
class Transaction(BaseModel):
    wallet = ForeignKeyField(Wallet, backref='transactions')
    amount = DecimalField(decimal_places=2)
    transaction_type = CharField()
    description = TextField(null=True)
    status = CharField(default='pending')
    created_at = DateTimeField(default=datetime.now)

# Initialize database
def initialize_db():
    db.connect()
    db.create_tables([User, Wallet, Transaction],safe=True)
    db.close()
initialize_db()