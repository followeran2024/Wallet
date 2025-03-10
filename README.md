# Wallet API

## Overview
This is a Flask-based Wallet API that provides functionalities for user authentication, wallet management, and transaction handling. The API uses OAuth2 for authentication and integrates with Peewee ORM for database interactions.

## Features
- User authentication via OAuth2 token validation.
- Create and retrieve wallets.
- Perform transactions (credit/debit) with balance validation.
- Retrieve transaction history with pagination.

## Requirements
- Python +3.8
- Flask
- Peewee ORM
- Requests
- Flask-CORS
- Python-dotenv

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and configure it with your database credentials and authentication service:
   ```ini
   DB_USERNAME=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   DB_NAME=your_db_name
   VALIDATE_TOKEN_URL=your_auth_service_url
   ```

5. Run the Flask application:
   ```bash
   flask run
   ```

## API Endpoints

### Authentication Middleware
All API routes require a valid OAuth2 token. The token should be passed in the request headers:
```http
Authorization: Bearer <your_token>
```

### Users
#### Create User
- **Endpoint:** `POST /api/users`
- **Request Body:**
  ```json
  {
    "username": "example_user",
    "email": "user@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User created successfully",
    "user": { "id": 1, "username": "example_user", "email": "user@example.com" }
  }
  ```

### Wallets
#### Create Wallet
- **Endpoint:** `POST /api/wallets`
- **Request Body:**
  ```json
  {
    "currency": "IRT"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Wallet created successfully",
    "wallet": { "id": 1, "currency": "IRT", "balance": 0.0 }
  }
  ```

#### Get Wallet
- **Endpoint:** `GET /api/wallets/<wallet_id>`
- **Response:**
  ```json
  {
    "id": 1,
    "currency": "USD",
    "balance": 100.0
  }
  ```

### Transactions
#### Create Transaction
- **Endpoint:** `POST /api/transactions`
- **Request Body:**
  ```json
  {
    "wallet_id": 1,
    "amount": 50.0,
    "transaction_type": "debit",
    "description": "Purchase"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Transaction completed successfully",
    "transaction": { "id": 1, "amount": 50.0, "transaction_type": "debit" },
    "new_balance": 50.0
  }
  ```

#### Get Transactions
- **Endpoint:** `GET /api/transactions?page=1&per_page=10`
- **Response:**
  ```json
  {
    "transactions": [
      { "id": 1, "amount": 50.0, "transaction_type": "debit" }
    ],
    "total_count": 1,
    "page": 1,
    "per_page": 10,
    "total_pages": 1
  }
  ```

## Logging
The API includes logging for important events, such as user creation, token validation, wallet transactions, and error handling. Logs are formatted as:
```
2025-01-01 12:00:00 - INFO - Validating OAuth2 token for endpoint: create_wallet
2025-01-01 12:00:01 - WARNING - Token validation failed
2025-01-01 12:00:02 - ERROR - Wallet not found
```

## Error Handling
The API returns meaningful error messages:
- `401 Unauthorized` for missing or invalid tokens.
- `400 Bad Request` for incorrect input.
- `404 Not Found` if a resource does not exist.
- `503 Service Unavailable` if the authentication service is down.


## Admin Blueprint
PREFIX : /admin

Entities (POST,GET,DELETE):
- Wallet 
- User 
- Transaction
  * Caution: by default rate limiting 10 requests per minute is defined for all admin endpoints.
### PROTECTION
Admin blueprint is protected by a static token in environment variables. For each request you header must include `X-Admin-Token` to authorize.
*** updating admin token, periodically is strongly recommended! ***
## Author
Amir Ahmadabadiha

