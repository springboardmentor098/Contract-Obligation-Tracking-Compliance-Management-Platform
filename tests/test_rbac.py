import asyncio
import httpx
from app.main import app


async def test_scenario_1_authorized_user():
    """Scenario 1 – Authorized User:
    Login as Administrator and access an Administrator-protected API (DELETE /users/{user_id}).
    Expected Result: 200 OK
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Login as Administrator
        login_response = await client.post(
            "/auth/login",
            json={"email": "admin@contractiq.com", "password": "password123"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
        token_data = login_response.json()
        access_token = token_data["access_token"]
        assert token_data["role"] == "Administrator"

        # 2. Access protected DELETE /users/99 endpoint with Administrator JWT
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.delete("/users/99", headers=headers)
        
        print(f"\n[Scenario 1 - Authorized User]")
        print(f"  User Role: Administrator")
        print(f"  Endpoint: DELETE /users/99")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"


async def test_scenario_2_unauthorized_authenticated_user():
    """Scenario 2 – Authenticated but Unauthorized User:
    Login as an Employee and attempt to access an Administrator-only API (DELETE /users/{user_id}).
    Expected Result: 403 Forbidden
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Login as Employee
        login_response = await client.post(
            "/auth/login",
            json={"email": "employee@contractiq.com", "password": "password123"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
        token_data = login_response.json()
        access_token = token_data["access_token"]
        assert token_data["role"] == "Employee"

        # 2. Attempt to access DELETE /users/99 endpoint with Employee JWT
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.delete("/users/99", headers=headers)

        print(f"\n[Scenario 2 - Authenticated but Unauthorized User]")
        print(f"  User Role: Employee")
        print(f"  Endpoint: DELETE /users/99")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")
        assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
        assert "Forbidden" in response.json()["detail"] or "permissions" in response.json()["detail"]


async def test_scenario_3_unauthenticated_user():
    """Scenario 3 – Unauthenticated User:
    Access a protected API without providing a valid JWT.
    Expected Result: 401 Unauthorized
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # Attempt to access DELETE /users/99 without Authorization header
        response = await client.delete("/users/99")

        print(f"\n[Scenario 3 - Unauthenticated User]")
        print(f"  User Role: Unauthenticated (No JWT)")
        print(f"  Endpoint: DELETE /users/99")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        assert "Not authenticated" in response.json()["detail"]


async def main():
    print("==================================================")
    print("  SPRINT 6 RBAC AUTHORIZATION TEST SUITE RESULTS  ")
    print("==================================================")
    
    await test_scenario_1_authorized_user()
    await test_scenario_2_unauthorized_authenticated_user()
    await test_scenario_3_unauthenticated_user()
    
    print("\n==================================================")
    print("[SUCCESS] ALL 3 MANDATED RBAC SCENARIOS PASSED 100% SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
