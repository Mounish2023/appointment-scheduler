
import asyncio
import httpx
import sys
import os

# Add project root to python path to potentially import modules if needed for setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

BASE_URL = "http://localhost:8000"

async def verify_auth():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Test Registration
        print("Testing Registration...")
        email = f"test_{os.urandom(4).hex()}@example.com"
        password = "strongpassword123"
        name = "Test User"
        
        register_payload = {
            "email": email,
            "password": password,
            "name": name
        }
        
        try:
            response = await client.post("/auth/register", json=register_payload)
            if response.status_code == 200:
                print(f"✅ Registration successful: {response.json()}")
            else:
                print(f"❌ Registration failed: {response.text}")
                return
        except Exception as e:
             print(f"❌ Connection failed: {e}")
             return

        # Test Login
        print("\nTesting Login...")
        login_data = {
            "username": email,
            "password": password
        }
        
        try:
            response = await client.post("/auth/login", data=login_data)
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ Login successful. Token: {token_data.get('access_token')[:20]}...")
            else:
                print(f"❌ Login failed: {response.text}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_auth())
