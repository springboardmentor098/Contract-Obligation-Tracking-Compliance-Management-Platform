import asyncio
import time
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_sprint8_workflow():

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        print("==================================================")
        print("  SPRINT 8: CONTRACT WORKFLOW TEST SUITE          ")
        print("==================================================")

        # 1. Login as Legal Manager (Authorized role for approval)
        mgr_login = await client.post(
            "/auth/login",
            json={"email": "legal.manager@contractiq.com", "password": "password123"}
        )
        assert mgr_login.status_code == 200, f"Manager login failed: {mgr_login.json()}"
        mgr_token = mgr_login.json()["access_token"]
        mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

        # 2. Login as Employee (Unauthorized role for approval)
        emp_login = await client.post(
            "/auth/login",
            json={"email": "employee@contractiq.com", "password": "password123"}
        )
        assert emp_login.status_code == 200, f"Employee login failed: {emp_login.json()}"
        emp_token = emp_login.json()["access_token"]
        emp_headers = {"Authorization": f"Bearer {emp_token}"}

        # Create contract for testing workflow
        cnt_num = f"CNT-SPRINT8-{int(time.time())}"
        create_resp = await client.post(
            "/contracts",
            json={
                "title": "Vendor SLA Agreement",
                "contract_number": cnt_num,
                "category": "Vendor Contract",
                "description": "IT Support Service Agreement",
                "start_date": "2026-08-01",
                "end_date": "2027-07-31"
            },
            headers=mgr_headers
        )
        assert create_resp.status_code == 201, f"Contract creation failed: {create_resp.json()}"
        contract = create_resp.json()
        contract_id = contract["id"]
        print(f"\n[Contract Created] ID={contract_id}, Status={contract['status']}")
        assert contract["status"] == "Draft"

        # Test 1 - Update Contract (PUT /contracts/{contract_id})
        update_resp = await client.put(
            f"/contracts/{contract_id}",
            json={
                "title": "Updated Vendor SLA Agreement",
                "category": "Service Agreement",
                "description": "Updated IT Support Service Agreement with 99.9% uptime"
            },
            headers=mgr_headers
        )
        print("\n[Test 1 – Update Contract]")
        print(f"  Status Code: {update_resp.status_code}")
        print(f"  Response Body: {update_resp.json()}")
        assert update_resp.status_code == 200
        updated_cnt = update_resp.json()
        assert updated_cnt["title"] == "Updated Vendor SLA Agreement"
        assert updated_cnt["category"] == "Service Agreement"

        # Test 5 (part A) - Invalid Status Transition Attempt (Draft -> Active directly)
        invalid_trans_resp = await client.post(
            f"/contracts/{contract_id}/activate",
            headers=mgr_headers
        )
        print("\n[Test 5 – Invalid Status Transition (Draft -> Active)]")
        print(f"  Status Code: {invalid_trans_resp.status_code}")
        print(f"  Response Body: {invalid_trans_resp.json()}")
        assert invalid_trans_resp.status_code == 400

        # Test 2 – Submit for Review (POST /contracts/{contract_id}/submit-review)
        submit_resp = await client.post(
            f"/contracts/{contract_id}/submit-review",
            headers=mgr_headers
        )
        print("\n[Test 2 – Submit Contract for Review]")
        print(f"  Status Code: {submit_resp.status_code}")
        print(f"  Response Body: {submit_resp.json()}")
        assert submit_resp.status_code == 200
        reviewed_cnt = submit_resp.json()
        assert reviewed_cnt["status"] == "Under Review"
        assert reviewed_cnt["reviewed_at"] is not None

        # Test 6 – Unauthorized Approval Attempt (Employee trying to approve)
        unauth_resp = await client.post(
            f"/contracts/{contract_id}/approve",
            headers=emp_headers
        )
        print("\n[Test 6 – Unauthorized Approval Attempt (Employee Role)]")
        print(f"  Status Code: {unauth_resp.status_code}")
        print(f"  Response Body: {unauth_resp.json()}")
        assert unauth_resp.status_code == 403, f"Expected 403 Forbidden, got {unauth_resp.status_code}"

        # Test 3 – Approve Contract (POST /contracts/{contract_id}/approve as Legal Manager)
        approve_resp = await client.post(
            f"/contracts/{contract_id}/approve",
            headers=mgr_headers
        )
        print("\n[Test 3 – Approve Contract (Manager Role)]")
        print(f"  Status Code: {approve_resp.status_code}")
        print(f"  Response Body: {approve_resp.json()}")
        assert approve_resp.status_code == 200
        approved_cnt = approve_resp.json()
        assert approved_cnt["status"] == "Approved"
        assert approved_cnt["approved_at"] is not None

        # Test 4 – Activate Contract (POST /contracts/{contract_id}/activate)
        activate_resp = await client.post(
            f"/contracts/{contract_id}/activate",
            headers=mgr_headers
        )
        print("\n[Test 4 – Activate Contract]")
        print(f"  Status Code: {activate_resp.status_code}")
        print(f"  Response Body: {activate_resp.json()}")
        assert activate_resp.status_code == 200
        active_cnt = activate_resp.json()
        assert active_cnt["status"] == "Active"

        # Test 7 – Contract Not Found
        not_found_resp = await client.get(
            "/contracts/999999",
            headers=mgr_headers
        )
        print("\n[Test 7 – Contract Not Found]")
        print(f"  Status Code: {not_found_resp.status_code}")
        print(f"  Response Body: {not_found_resp.json()}")
        assert not_found_resp.status_code == 404

        print("\n==================================================")
        print("[SUCCESS] ALL SPRINT 8 WORKFLOW TESTS PASSED 100% SUCCESSFULLY!")
        print("==================================================")


if __name__ == "__main__":
    asyncio.run(test_sprint8_workflow())
