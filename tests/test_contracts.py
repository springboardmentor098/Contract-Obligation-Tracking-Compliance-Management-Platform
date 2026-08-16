import time
import asyncio
import httpx
from app.main import app


async def test_create_contract_authenticated():
    """Test 1: Authenticated user creates a new contract (POST /contracts).
    Expected Result: 201 Created with full contract representation and auto-assigned created_by.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Login to obtain access token
        login_resp = await client.post(
            "/auth/login",
            json={"email": "Rathna@ex.com", "password": "password123"}
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.json()}"
        token_data = login_resp.json()
        token = token_data["access_token"]
        expected_user_id = token_data["user_id"]

        cnt_num = f"CNT-SPRINT7-{int(time.time())}"

        # 2. POST /contracts with valid contract payload
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "ABC Vendor Agreement",
            "contract_number": cnt_num,
            "category": "Vendor Contract",
            "description": "Annual vendor service agreement for IT infrastructure",
            "start_date": "2026-08-01",
            "end_date": "2027-07-31"
        }
        response = await client.post("/contracts", json=payload, headers=headers)

        print("\n[Test 1 - Create Contract Authenticated]")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")

        assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
        data = response.json()
        assert data["title"] == "ABC Vendor Agreement"
        assert data["contract_number"] == cnt_num
        assert data["category"] == "Vendor Contract"
        assert data["status"] == "Draft"
        assert data["created_by"] == expected_user_id
        assert "id" in data

        return data["id"], cnt_num, token


async def test_create_contract_duplicate_number(cnt_num: str, token: str):
    """Test 2: Creating contract with duplicate contract_number.
    Expected Result: 400 Bad Request.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "Duplicate Vendor Agreement",
            "contract_number": cnt_num,  # Duplicate number
            "category": "Vendor Contract",
            "description": "Duplicate contract test payload",
            "start_date": "2026-08-01",
            "end_date": "2027-07-31"
        }
        response = await client.post("/contracts", json=payload, headers=headers)

        print("\n[Test 2 - Duplicate Contract Number]")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")

        assert response.status_code == 400, f"Expected 400 Bad Request, got {response.status_code}"
        assert "already exists" in response.json()["detail"]


async def test_get_all_contracts(token: str):
    """Test 3: Retrieve all contracts (GET /contracts).
    Expected Result: 200 OK with list of contracts.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/contracts", headers=headers)

        print("\n[Test 3 - Get All Contracts]")
        print(f"  Status Code: {response.status_code}")
        print(f"  Contracts Count: {len(response.json())}")

        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        contracts = response.json()
        assert isinstance(contracts, list)
        assert len(contracts) > 0


async def test_get_contract_by_id(contract_id: int, cnt_num: str, token: str):
    """Test 4: Get specific contract by ID (GET /contracts/{contract_id}).
    Expected Result: 200 OK with contract object.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"/contracts/{contract_id}", headers=headers)

        print(f"\n[Test 4 - Get Contract by ID #{contract_id}]")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")

        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        data = response.json()
        assert data["id"] == contract_id
        assert data["contract_number"] == cnt_num


async def test_get_non_existent_contract(token: str):
    """Test 5: Retrieve non-existent contract ID (GET /contracts/999999).
    Expected Result: 404 Not Found.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/contracts/999999", headers=headers)

        print("\n[Test 5 - Non-Existent Contract ID]")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")

        assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
        assert "not found" in response.json()["detail"].lower()


async def test_unauthenticated_requests():
    """Test 6: Accessing protected endpoints without valid authentication token.
    Expected Result: 401 Unauthorized.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Unauthenticated POST /contracts
        post_resp = await client.post("/contracts", json={"title": "Test"})
        assert post_resp.status_code == 401, f"Expected 401, got {post_resp.status_code}"

        # 2. Unauthenticated GET /contracts
        get_all_resp = await client.get("/contracts")
        assert get_all_resp.status_code == 401, f"Expected 401, got {get_all_resp.status_code}"

        # 3. Unauthenticated GET /contracts/1
        get_id_resp = await client.get("/contracts/1")
        assert get_id_resp.status_code == 401, f"Expected 401, got {get_id_resp.status_code}"

        print("\n[Test 6 - Unauthenticated Requests]")
        print("  POST /contracts without token -> 401 Unauthorized [PASSED]")
        print("  GET /contracts without token -> 401 Unauthorized [PASSED]")
        print("  GET /contracts/1 without token -> 401 Unauthorized [PASSED]")


async def test_invalid_schema_validation(token: str):
    """Test 7: Missing required payload fields (POST /contracts).
    Expected Result: 422 Unprocessable Entity.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        headers = {"Authorization": f"Bearer {token}"}
        # Missing 'category' and 'contract_number'
        invalid_payload = {
            "title": "Incomplete Contract Request"
        }
        response = await client.post("/contracts", json=invalid_payload, headers=headers)

        print("\n[Test 7 - Missing Required Data Validation]")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Body: {response.json()}")

        assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"


async def main():
    print("==================================================")
    print("  SPRINT 7 CONTRACT REPOSITORY TEST SUITE         ")
    print("==================================================")

    contract_id, cnt_num, token = await test_create_contract_authenticated()
    await test_create_contract_duplicate_number(cnt_num, token)
    await test_get_all_contracts(token)
    await test_get_contract_by_id(contract_id, cnt_num, token)
    await test_get_non_existent_contract(token)
    await test_unauthenticated_requests()
    await test_invalid_schema_validation(token)

    print("\n==================================================")
    print("[SUCCESS] ALL SPRINT 7 CONTRACT MANAGEMENT TESTS PASSED 100% SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
