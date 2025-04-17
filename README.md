# login_system

A secure authentication system with mobile verification, OTP, and login security mechanisms.

## Setup

```bash

# do this once
python3 -m venv .venv

source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

# do this once
pip install -r requirements.txt

# run migrations
python manage.py migrate
```

## Features
-  Mobile number registration/verification
-  OTP (One-Time Password) generation and validation
-  Password-based login
-  Profile completion flow
-  Brute-force attack protection
-  IP-based rate limiting
-  Token-based authentication

## API Endpoints

### `POST /api/users/auth/check-mobile`
Check if mobile number is registered.

### `POST /api/users/auth/verify-otp`
Verify OTP for new users.

### `POST /api/users/auth/login`
Login for existing users.

### `PUT /api/users/auth/complete-profile`
Complete profile for new users.

## Request/Response Examples
checkout the postman collection.

