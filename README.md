# InkOdyssey Backend - Simple Authentication API# InkOdyssey Backend - Authentication API



A streamlined Django REST Framework backend with JWT authentication.A comprehensive Django REST Framework backend with JWT authentication and social login (Google & Facebook).



## ✨ Features## Features



- ✅ Email-based authentication (no username required)✅ **Custom User Model** - Email-based authentication with first name and last name

- ✅ JWT tokens with automatic refresh✅ **JWT Authentication** - Secure token-based authentication with refresh tokens

- ✅ User registration with email, first name, last name, password✅ **Social Login** - Google OAuth2 and Facebook OAuth2 integration

- ✅ User login and logout✅ **User Registration** - Sign up with email, password, first name, and last name

- ✅ User profile management✅ **User Login** - Email and password authentication

- ✅ Password change functionality✅ **Token Refresh** - Automatic token refresh for seamless sessions

- ✅ CORS enabled for frontend integration✅ **Password Change** - Secure password update for authenticated users

✅ **User Profile** - Get and update user details

## 🚀 Quick Start✅ **CORS Enabled** - Ready for frontend integration



```bash## Tech Stack

# 1. Copy environment file

cp .env.example .env- **Django 4.2** - Python web framework

- **Django REST Framework** - API toolkit

# 2. Run migrations (already done)- **djangorestframework-simplejwt** - JWT authentication

python manage.py migrate- **django-allauth** - Social authentication

- **dj-rest-auth** - REST API endpoints for auth

# 3. Create superuser (optional)- **django-cors-headers** - CORS handling

python manage.py createsuperuser- **python-decouple** - Configuration management



# 4. Start server## Project Structure

python manage.py runserver

``````

backend/

Server runs at: **http://localhost:8000**├── backend/              # Main project settings

│   ├── settings.py       # Django configuration

## 📡 API Endpoints│   ├── urls.py          # Main URL routing

│   └── wsgi.py          # WSGI configuration

| Endpoint | Method | Auth | Description |├── users/               # Users app

|----------|--------|------|-------------|│   ├── models.py        # Custom User model

| `/api/auth/register/` | POST | No | Register new user |│   ├── serializers.py   # DRF serializers

| `/api/auth/login/` | POST | No | Login user |│   ├── views.py         # API views

| `/api/auth/logout/` | POST | Yes | Logout user |│   ├── urls.py          # Auth URL patterns

| `/api/auth/user/` | GET/PUT/PATCH | Yes | Get/update profile |│   └── admin.py         # Admin configuration

| `/api/auth/change-password/` | POST | Yes | Change password |├── manage.py            # Django management script

| `/api/auth/token/refresh/` | POST | No | Refresh JWT token |├── .env.example         # Environment variables template

| `/admin/` | GET | Yes | Admin panel |└── db.sqlite3          # SQLite database

```

## 📝 API Examples

## Setup Instructions

### Register

```bash### 1. Environment Setup

POST /api/auth/register/

{Copy `.env.example` to `.env` and configure:

  "email": "user@example.com",

  "first_name": "John",```bash

  "last_name": "Doe",cp .env.example .env

  "password": "SecurePass123!",```

  "password2": "SecurePass123!"

}Update `.env` with your credentials:

``````env

SECRET_KEY=your-django-secret-key

**Response:**DEBUG=True

```jsonALLOWED_HOSTS=localhost,127.0.0.1

{CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

  "user": {GOOGLE_CLIENT_ID=your-google-client-id

    "id": 1,GOOGLE_CLIENT_SECRET=your-google-client-secret

    "email": "user@example.com",FACEBOOK_CLIENT_ID=your-facebook-app-id

    "first_name": "John",FACEBOOK_CLIENT_SECRET=your-facebook-app-secret

    "last_name": "Doe",```

    "full_name": "John Doe",

    "date_joined": "2025-10-15T12:00:00Z"### 2. Database Setup

  },

  "tokens": {Migrations have already been applied. If you need to reset:

    "refresh": "eyJ0eXAiOiJKV1Qi...",

    "access": "eyJ0eXAiOiJKV1Qi..."```bash

  },python manage.py makemigrations

  "message": "User registered successfully"python manage.py migrate

}```

```

### 3. Create Superuser

### Login

```bash```bash

POST /api/auth/login/python manage.py createsuperuser

{```

  "email": "user@example.com",

  "password": "SecurePass123!"### 4. Run Development Server

}

``````bash

python manage.py runserver

### Get User Profile (Authenticated)```

```bash

GET /api/auth/user/The API will be available at `http://localhost:8000`

Headers:

  Authorization: Bearer <access_token>## API Endpoints

```

### Authentication

### Refresh Token

```bash#### Register a New User

POST /api/auth/token/refresh/```http

{POST /api/auth/register/

  "refresh": "eyJ0eXAiOiJKV1Qi..."Content-Type: application/json

}

```{

  "email": "user@example.com",

## 🧪 Testing  "first_name": "John",

  "last_name": "Doe",

Use the included test script:  "password": "securepassword123",

```bash  "password2": "securepassword123"

python test_api.py}

``````



Or use cURL:**Response:**

```bash```json

curl -X POST http://localhost:8000/api/auth/register/ \{

  -H "Content-Type: application/json" \  "user": {

  -d '{"email":"test@example.com","first_name":"Test","last_name":"User","password":"testpass123","password2":"testpass123"}'    "id": 1,

```    "email": "user@example.com",

    "first_name": "John",

## 🔒 Security    "last_name": "Doe",

    "full_name": "John Doe",

- Passwords hashed with PBKDF2    "date_joined": "2025-10-15T12:00:00Z",

- JWT token authentication    "provider": null

- Token blacklisting on logout  },

- CORS configured  "tokens": {

- Email validation    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",

- Password strength validation    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."

  },

## 🛠️ Tech Stack  "message": "User registered successfully"

}

- Django 4.2```

- Django REST Framework

- djangorestframework-simplejwt#### Login

- django-cors-headers```http

- python-decouplePOST /api/auth/login/

Content-Type: application/json

## 📖 More Documentation

{

- **QUICKSTART.md** - Quick setup guide  "email": "user@example.com",

- **IMPLEMENTATION_SUMMARY.md** - Technical details  "password": "securepassword123"

- **.env.example** - Environment configuration}

```

## 🌐 Frontend Integration

**Response:**

```javascript```json

// Register{

const response = await fetch('http://localhost:8000/api/auth/register/', {  "user": {

  method: 'POST',    "id": 1,

  headers: { 'Content-Type': 'application/json' },    "email": "user@example.com",

  body: JSON.stringify({    "first_name": "John",

    email: 'user@example.com',    "last_name": "Doe",

    first_name: 'John',    "full_name": "John Doe"

    last_name: 'Doe',  },

    password: 'SecurePass123!',  "tokens": {

    password2: 'SecurePass123!'    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",

  })    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."

});  },

const { user, tokens } = await response.json();  "message": "Login successful"

}

// Store tokens```

localStorage.setItem('accessToken', tokens.access);

localStorage.setItem('refreshToken', tokens.refresh);#### Refresh Token

```http

// Authenticated requestsPOST /api/auth/token/refresh/

const userResponse = await fetch('http://localhost:8000/api/auth/user/', {Content-Type: application/json

  headers: {

    'Authorization': `Bearer ${tokens.access}`,{

    'Content-Type': 'application/json'  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."

  }}

});```

```

#### Logout
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### User Management

#### Get User Profile
```http
GET /api/auth/user/
Authorization: Bearer <access_token>
```

#### Update User Profile
```http
PUT /api/auth/user/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

#### Change Password
```http
POST /api/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "oldpassword123",
  "new_password": "newpassword456",
  "new_password2": "newpassword456"
}
```

### Social Authentication

#### Google Login
```http
GET /api/auth/social/google/
```

#### Facebook Login
```http
GET /api/auth/social/facebook/
```

## Setting Up Social Authentication

### Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/social/google/callback/`
   - `http://localhost:3000` (your frontend URL)
6. Copy Client ID and Client Secret to `.env`

### Facebook OAuth2

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Configure OAuth redirect URIs:
   - `http://localhost:8000/api/auth/social/facebook/callback/`
5. Copy App ID and App Secret to `.env`

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Get User (with token)
```bash
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Security Notes

- ✅ Passwords are hashed using Django's default hasher (PBKDF2)
- ✅ JWT tokens are signed and verified
- ✅ CORS is configured for specific origins
- ✅ Token blacklisting enabled for logout
- ✅ Email validation on registration
- ✅ Password validation (minimum length, common passwords, etc.)

## Development Tips

### Access Admin Panel
Visit `http://localhost:8000/admin/` and login with superuser credentials.

### Check Installed Packages
```bash
pip list
```

### Run Tests
```bash
python manage.py test users
```

### Create New Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### Issue: Import errors or missing modules
**Solution:** Ensure all packages are installed in your virtual environment:
```bash
pip install -r requirements.txt
```

### Issue: CORS errors from frontend
**Solution:** Update `CORS_ALLOWED_ORIGINS` in `.env` with your frontend URL

### Issue: Social login not working
**Solution:** 
1. Verify OAuth credentials in `.env`
2. Check redirect URIs match in provider console
3. Ensure provider apps are enabled in Django admin

## Next Steps

- [ ] Create `requirements.txt` with all dependencies
- [ ] Add email verification for registration
- [ ] Implement password reset functionality
- [ ] Add rate limiting to prevent abuse
- [ ] Set up production database (PostgreSQL)
- [ ] Configure static/media files for production
- [ ] Add comprehensive test coverage
- [ ] Set up CI/CD pipeline

## License

This project is part of the InkOdyssey application.
