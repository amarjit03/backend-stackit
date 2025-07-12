#!/usr/bin/env python3
"""
Basic test script for StackIt Backend
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_api():
    """Test basic API endpoints"""
    async with httpx.AsyncClient() as client:
        print("Testing StackIt Backend API...")
        
        # Test root endpoint
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"✓ Root endpoint: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"✗ Root endpoint failed: {e}")
        
        # Test health check
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✓ Health check: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
        
        # Test API docs
        try:
            response = await client.get(f"{BASE_URL}/docs")
            print(f"✓ API docs: {response.status_code}")
        except Exception as e:
            print(f"✗ API docs failed: {e}")
        
        # Test user registration
        try:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
            print(f"✓ User registration: {response.status_code}")
            if response.status_code == 201:
                print(f"  User created: {response.json()['username']}")
            elif response.status_code == 400:
                print(f"  User already exists (expected)")
        except Exception as e:
            print(f"✗ User registration failed: {e}")
        
        # Test user login
        try:
            login_data = {
                "username": "testuser",
                "password": "testpassword123"
            }
            response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            print(f"✓ User login: {response.status_code}")
            if response.status_code == 200:
                token = response.json()["access_token"]
                print(f"  Token received: {token[:20]}...")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
                print(f"✓ Get current user: {response.status_code}")
                if response.status_code == 200:
                    print(f"  User: {response.json()['username']}")
        except Exception as e:
            print(f"✗ User login failed: {e}")
        
        # Test get topics
        try:
            response = await client.get(f"{BASE_URL}/api/v1/mcq/topics")
            print(f"✓ Get MCQ topics: {response.status_code}")
            if response.status_code == 200:
                topics = response.json()
                print(f"  Available topics: {topics}")
        except Exception as e:
            print(f"✗ Get MCQ topics failed: {e}")

if __name__ == "__main__":
    print("Make sure the server is running on http://localhost:8000")
    print("Run: python run.py")
    print("-" * 50)
    asyncio.run(test_api())

