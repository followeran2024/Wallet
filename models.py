from peewee import *
from datetime import datetime, timezone
from playhouse.pool import PooledMySQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()
from playhouse.shortcuts import ReconnectMixin

# Create a ReconnectMixin database class
class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    def __init__(self, *args, autoreconnect=True, reconnect_retries=5, 
                 reconnect_interval=1, **kwargs):
        # These parameters are for ReconnectMixin
        self.autoreconnect = autoreconnect
        self.reconnect_retries = reconnect_retries
        self.reconnect_interval = reconnect_interval
        
        # Remove ReconnectMixin-specific args before passing to MySQLDatabase
        kwargs.pop('autoreconnect', None)
        kwargs.pop('reconnect_retries', None)
        kwargs.pop('reconnect_interval', None)
        
        super().__init__(*args, **kwargs)

db = ReconnectMySQLDatabase(autoconnect=True,database='wallet',user=str(os.getenv('DB_USERNAME')),password=str(os.getenv('DB_PASSWORD')),
    host=str(os.getenv('DB_HOST')),
    port=int(os.getenv('DB_PORT')),
    autoreconnect=True, 
    reconnect_retries=5,  
    reconnect_interval=1)

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