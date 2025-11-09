"""
Test script for Diary API endpoints
Run this after starting the Django server with: py manage.py runserver
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api"

# Test credentials - update these with your actual credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def print_response(response, title):
    """Helper function to print formatted responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_diary_api():
    """Test the diary API endpoints"""
    
    # Step 1: Login to get access token
    print("\n🔐 Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed. Please update TEST_EMAIL and TEST_PASSWORD with valid credentials.")
        print_response(login_response, "Login Response")
        return
    
    # Get access token
    access_token = login_response.json()["tokens"]["access"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("✅ Login successful!")
    
    # Step 2: Create a diary entry
    print("\n📝 Creating a diary entry...")
    create_response = requests.post(
        f"{BASE_URL}/diary/entries/",
        headers=headers,
        json={
            "title": "Test Diary Entry",
            "content_blocks": [
                {
                    "block_type": "text",
                    "order": 0,
                    "text_content": "This is my first diary entry created via API!"
                },
                {
                    "block_type": "text",
                    "order": 1,
                    "text_content": "I'm testing the InkOdyssey diary app."
                }
            ]
        }
    )
    print_response(create_response, "Create Diary Entry")
    
    if create_response.status_code == 201:
        entry_id = create_response.json()["id"]
        print(f"✅ Diary entry created with ID: {entry_id}")
        
        # Step 3: Get the created entry
        print(f"\n📖 Fetching diary entry {entry_id}...")
        get_response = requests.get(
            f"{BASE_URL}/diary/entries/{entry_id}/",
            headers=headers
        )
        print_response(get_response, f"Get Diary Entry {entry_id}")
        
        # Step 4: List all entries
        print("\n📚 Listing all diary entries...")
        list_response = requests.get(
            f"{BASE_URL}/diary/entries/",
            headers=headers
        )
        print_response(list_response, "List All Diary Entries")
        
        # Step 5: Add a content block
        print(f"\n➕ Adding a content block to entry {entry_id}...")
        add_block_response = requests.post(
            f"{BASE_URL}/diary/entries/{entry_id}/blocks/",
            headers=headers,
            json={
                "block_type": "text",
                "order": 2,
                "text_content": "This is an additional content block added later!"
            }
        )
        print_response(add_block_response, "Add Content Block")
        
        # Step 6: Get diary statistics
        print("\n📊 Getting diary statistics...")
        stats_response = requests.get(
            f"{BASE_URL}/diary/stats/",
            headers=headers
        )
        print_response(stats_response, "Diary Statistics")
        
        # Step 7: Update the entry
        print(f"\n✏️ Updating diary entry {entry_id}...")
        update_response = requests.patch(
            f"{BASE_URL}/diary/entries/{entry_id}/",
            headers=headers,
            json={
                "title": "Updated Test Diary Entry"
            }
        )
        print_response(update_response, "Update Diary Entry")
        
        # Step 8: Get entries by date (today)
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        print(f"\n📅 Getting entries for date: {today}...")
        by_date_response = requests.get(
            f"{BASE_URL}/diary/entries/by-date/?date={today}",
            headers=headers
        )
        print_response(by_date_response, f"Entries for {today}")
        
        # Step 9: Delete the entry (optional - uncomment to test)
        # print(f"\n🗑️ Deleting diary entry {entry_id}...")
        # delete_response = requests.delete(
        #     f"{BASE_URL}/diary/entries/{entry_id}/",
        #     headers=headers
        # )
        # print_response(delete_response, "Delete Diary Entry")
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
    else:
        print("❌ Failed to create diary entry")

if __name__ == "__main__":
    print("🚀 Starting Diary API Tests")
    print("="*60)
    print("Make sure the Django server is running on http://localhost:8000")
    print("Update TEST_EMAIL and TEST_PASSWORD with valid credentials")
    
    try:
        test_diary_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure Django is running: py manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
