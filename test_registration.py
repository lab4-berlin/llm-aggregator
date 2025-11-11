#!/usr/bin/env python3
"""
Test script for registration flow (happy path):
1. Register a new user
2. Get verification token from logs/DB
3. Verify email
4. Login
5. Logout
"""

import requests
import json
import sys
from datetime import datetime

API_URL = "http://localhost:8000"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print(f"{'='*60}")

def test_registration():
    """Test the complete registration and login flow."""
    
    # Step 1: Register
    print_step(1, "Registering a new user")
    register_data = {
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }
    
    print(f"Registering with: {register_data['email']}")
    response = requests.post(f"{API_URL}/api/auth/register", json=register_data)
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.json())
        return False
    
    result = response.json()
    print(f"✅ Registration successful!")
    print(f"   Message: {result.get('message')}")
    print(f"   User ID: {result.get('user_id')}")
    print(f"\n📧 Check backend logs for verification email link")
    print(f"   (If SMTP not configured, the link will be in the logs)")
    
    # Get verification token from database (for testing)
    # In real scenario, user clicks link from email
    print(f"\n⚠️  For testing, you need to:")
    print(f"   1. Check backend logs for the verification URL")
    print(f"   2. Or query the database for email_verification_token")
    print(f"   3. Then use that token to verify email")
    
    verification_token = input("\nEnter verification token from logs/DB (or press Enter to skip): ").strip()
    
    if not verification_token:
        print("⚠️  Skipping email verification step")
        return False
    
    # Step 2: Verify Email
    print_step(2, "Verifying email")
    verify_data = {"token": verification_token}
    response = requests.post(f"{API_URL}/api/auth/verify-email", json=verify_data)
    
    if response.status_code != 200:
        print(f"❌ Email verification failed: {response.status_code}")
        print(response.json())
        return False
    
    result = response.json()
    print(f"✅ Email verified successfully!")
    print(f"   User: {result.get('user', {}).get('email')}")
    
    # Step 3: Login
    print_step(3, "Logging in")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.json())
        return False
    
    result = response.json()
    token = result.get("access_token")
    user = result.get("user")
    
    print(f"✅ Login successful!")
    print(f"   User: {user.get('email')}")
    print(f"   Name: {user.get('name')}")
    print(f"   Token: {token[:20]}...")
    
    # Step 4: Get current user (verify token works)
    print_step(4, "Getting current user info")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/api/auth/me", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Get user failed: {response.status_code}")
        print(response.json())
        return False
    
    result = response.json()
    print(f"✅ User info retrieved!")
    print(f"   Email: {result.get('email')}")
    print(f"   Name: {result.get('name')}")
    print(f"   Verified: {result.get('email_verified')}")
    
    # Step 5: Logout (client-side, but we can test the endpoint)
    print_step(5, "Logging out")
    response = requests.post(f"{API_URL}/api/auth/logout", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Logout failed: {response.status_code}")
        print(response.json())
        return False
    
    print(f"✅ Logout successful!")
    print(f"   (Token should be removed client-side)")
    
    # Verify token is invalid
    print(f"\n🔍 Verifying token is invalid after logout...")
    response = requests.get(f"{API_URL}/api/auth/me", headers=headers)
    if response.status_code == 401:
        print(f"✅ Token correctly invalidated")
    else:
        print(f"⚠️  Token still valid (logout is client-side only)")
    
    print(f"\n{'='*60}")
    print("✅ All tests passed!")
    print(f"{'='*60}")
    return True

if __name__ == "__main__":
    try:
        # Check if API is running
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"❌ API health check failed")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {API_URL}")
        print(f"   Make sure the backend is running: docker-compose up")
        sys.exit(1)
    
    success = test_registration()
    sys.exit(0 if success else 1)

