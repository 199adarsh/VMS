#!/usr/bin/env python3
"""
Test script to verify the local setup works before deploying to Vercel
"""
import requests
import json

def test_local_api():
    """Test the local API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing local API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
        else:
            print(f"Health error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test simple endpoint
    try:
        response = requests.get(f"{base_url}/test")
        print(f"Test endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Test response: {response.json()}")
        else:
            print(f"Test error: {response.text}")
    except Exception as e:
        print(f"Test endpoint failed: {e}")
    
    # Test login endpoint (should fail with no credentials)
    try:
        response = requests.post(f"{base_url}/login", json={"email": "test", "password": "test"})
        print(f"Login test: {response.status_code}")
        if response.status_code == 401:
            print("Login correctly rejected invalid credentials")
        else:
            print(f"Login response: {response.json()}")
    except Exception as e:
        print(f"Login test failed: {e}")

if __name__ == "__main__":
    test_local_api()
