import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_api():
    session = requests.Session()
    
    print("Testing Volunteer Management System API")
    print("=" * 50)
    
    # Test 1: Login as volunteer
    print("\n1. Testing login as volunteer...")
    login_data = {
        "email": "volunteer1@example.com",
        "password": "password123"
    }
    
    response = session.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        print(f"Login successful: {response.json()}")
    else:
        print(f"Login failed: {response.text}")
        return
    
    # Test 2: Get assigned tasks
    print("\n2. Testing get assigned tasks...")
    response = session.get(f"{BASE_URL}/tasks/assigned")
    print(f"Assigned tasks response: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"Found {len(tasks)} assigned tasks")
        for task in tasks:
            print(f"  - {task.get('title', 'Unknown')} (Status: {task.get('status', 'Unknown')})")
    else:
        print(f"Failed to get tasks: {response.text}")
    
    # Test 3: Get profile
    print("\n3. Testing get profile...")
    response = session.get(f"{BASE_URL}/profile")
    print(f"Profile response: {response.status_code}")
    if response.status_code == 200:
        profile = response.json()
        print(f"Profile: {profile.get('name', 'Unknown')} ({profile.get('role', 'Unknown')})")
    else:
        print(f"Failed to get profile: {response.text}")
    
    # Test 4: Logout
    print("\n4. Testing logout...")
    response = session.post(f"{BASE_URL}/logout")
    print(f"Logout response: {response.status_code}")
    if response.status_code == 200:
        print("Logout successful")
    else:
        print(f"Logout failed: {response.text}")
    
    # Test 5: Try to access protected endpoint after logout
    print("\n5. Testing access after logout...")
    response = session.get(f"{BASE_URL}/tasks/assigned")
    print(f"Protected endpoint response: {response.status_code}")
    if response.status_code == 401:
        print("Correctly blocked access after logout")
    else:
        print(f"Unexpected response: {response.text}")
    
    print("\n" + "=" * 50)
    print("API test completed!")

if __name__ == "__main__":
    test_api() 