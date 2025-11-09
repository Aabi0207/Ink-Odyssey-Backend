"""
Quick Test Script for Authentication API
Run this after starting the server to test the endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_auth_flow():
    """Test the complete authentication flow"""
    
    # Test data
    user_data = {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123!",
        "password2": "TestPass123!"
    }
    
    # 1. Register
    print("\n🔹 Testing User Registration...")
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)
    print_response("REGISTER", response)
    
    if response.status_code == 201:
        data = response.json()
        access_token = data.get('tokens', {}).get('access')
        refresh_token = data.get('tokens', {}).get('refresh')
        
        # 2. Get User Profile
        print("\n🔹 Testing Get User Profile...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/user/", headers=headers)
        print_response("GET USER PROFILE", response)
        
        # 3. Update User Profile
        print("\n🔹 Testing Update User Profile...")
        update_data = {"first_name": "Updated", "last_name": "Name"}
        response = requests.patch(
            f"{BASE_URL}/api/auth/user/", 
            json=update_data, 
            headers=headers
        )
        print_response("UPDATE USER PROFILE", response)
        
        # 4. Token Refresh
        print("\n🔹 Testing Token Refresh...")
        response = requests.post(
            f"{BASE_URL}/api/auth/token/refresh/",
            json={"refresh": refresh_token}
        )
        print_response("TOKEN REFRESH", response)
        
        if response.status_code == 200:
            new_access_token = response.json().get('access')
            headers = {"Authorization": f"Bearer {new_access_token}"}
        
        # 5. Logout
        print("\n🔹 Testing Logout...")
        response = requests.post(
            f"{BASE_URL}/api/auth/logout/",
            json={"refresh_token": refresh_token},
            headers=headers
        )
        print_response("LOGOUT", response)
    
    # 6. Login with existing user
    print("\n🔹 Testing User Login...")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print_response("LOGIN", response)
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("InkOdyssey Backend - Authentication API Test")
    print("="*60)
    print("\n⚠️  Make sure the Django server is running:")
    print("   python manage.py runserver")
    print("\nStarting tests in 3 seconds...")
    
    import time
    time.sleep(3)
    
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server!")
        print("Please start the server with: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
