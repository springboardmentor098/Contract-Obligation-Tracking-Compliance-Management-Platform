import asyncio
import time
from datetime import date, timedelta
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_sprint9_obligations():

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        print("==================================================")
        print("  SPRINT 9: OBLIGATION TRACKING MODULE TEST SUITE ")
        print("==================================================")

        # 1. Login to get authentication token
        login_resp = await client.post(
            "/auth/login",
            json={"email": "contract.manager@contractiq.com", "password": "password123"}
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.json()}"
        token_data = login_resp.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch valid user ID from DB users list
        users_resp = await client.get("/users", headers=headers)
        if users_resp.status_code == 200 and len(users_resp.json()) > 0:
            user_id = users_resp.json()[0].get("user_id") or users_resp.json()[0].get("id", 1)
        else:
            user_id = 1

        # 2. Create a contract for attaching obligations
        cnt_num = f"CNT-SPRINT9-{int(time.time())}"
        contract_resp = await client.post(
            "/contracts",
            json={
                "title": "ABC Vendor Agreement",
                "contract_number": cnt_num,
                "category": "Vendor Contract",
                "description": "Obligation testing parent contract",
                "start_date": "2026-08-01",
                "end_date": "2027-07-31"
            },
            headers=headers
        )
        assert contract_resp.status_code == 201, f"Contract creation failed: {contract_resp.json()}"
        contract_id = contract_resp.json()["id"]

        # Test 9 – Unauthenticated Request (POST /obligations without token)
        unauth_resp = await client.post(
            "/obligations",
            json={
                "contract_id": contract_id,
                "title": "Unauthenticated Obligation",
                "obligation_type": "Reporting Requirement",
                "assigned_to": user_id
            }
        )
        print("\n[Test 9 – Unauthenticated Request]")
        print(f"  Status Code: {unauth_resp.status_code}")
        assert unauth_resp.status_code == 401

        # Test 1 – Create Obligation (POST /obligations)
        future_due = str(date.today() + timedelta(days=10))
        create_ob_resp = await client.post(
            "/obligations",
            json={
                "contract_id": contract_id,
                "title": "Submit Monthly Service Report",
                "description": "Vendor must submit the monthly service report.",
                "obligation_type": "Reporting Requirement",
                "due_date": future_due,
                "assigned_to": user_id
            },
            headers=headers
        )
        print("\n[Test 1 – Create Obligation]")
        print(f"  Status Code: {create_ob_resp.status_code}")
        print(f"  Response Body: {create_ob_resp.json()}")
        assert create_ob_resp.status_code == 201
        ob1 = create_ob_resp.json()
        ob1_id = ob1["id"]
        assert ob1["title"] == "Submit Monthly Service Report"
        assert ob1["status"] == "Pending"
        assert ob1["contract_id"] == contract_id

        # Test 2 – Get All Obligations (GET /obligations)
        get_all_resp = await client.get("/obligations", headers=headers)
        print("\n[Test 2 – Get All Obligations]")
        print(f"  Status Code: {get_all_resp.status_code}")
        print(f"  Obligations Count: {len(get_all_resp.json())}")
        assert get_all_resp.status_code == 200
        assert isinstance(get_all_resp.json(), list)

        # Test 3 – Get Obligation by ID (GET /obligations/{obligation_id})
        get_id_resp = await client.get(f"/obligations/{ob1_id}", headers=headers)
        print(f"\n[Test 3 – Get Obligation by ID #{ob1_id}]")
        print(f"  Status Code: {get_id_resp.status_code}")
        print(f"  Response Body: {get_id_resp.json()}")
        assert get_id_resp.status_code == 200
        assert get_id_resp.json()["id"] == ob1_id

        # Test 4 – Get Obligations for a Specific Contract (GET /contracts/{contract_id}/obligations)
        get_cnt_obs_resp = await client.get(f"/contracts/{contract_id}/obligations", headers=headers)
        print(f"\n[Test 4 – Get Contract Obligations for Contract #{contract_id}]")
        print(f"  Status Code: {get_cnt_obs_resp.status_code}")
        print(f"  Response Body: {get_cnt_obs_resp.json()}")
        assert get_cnt_obs_resp.status_code == 200
        assert len(get_cnt_obs_resp.json()) >= 1

        # Test 5 – Update Obligation (PUT /obligations/{obligation_id})
        update_ob_resp = await client.put(
            f"/obligations/{ob1_id}",
            json={
                "title": "Submit Monthly Service & SLA Performance Report",
                "description": "Vendor must submit monthly service and SLA performance report.",
                "obligation_type": "Service Level Agreement"
            },
            headers=headers
        )
        print("\n[Test 5 – Update Obligation]")
        print(f"  Status Code: {update_ob_resp.status_code}")
        print(f"  Response Body: {update_ob_resp.json()}")
        assert update_ob_resp.status_code == 200
        assert update_ob_resp.json()["title"] == "Submit Monthly Service & SLA Performance Report"
        assert update_ob_resp.json()["obligation_type"] == "Service Level Agreement"

        # Test 6 – Update Obligation Status (PATCH /obligations/{obligation_id}/status)
        status_patch_resp = await client.patch(
            f"/obligations/{ob1_id}/status",
            json={"status": "In Progress"},
            headers=headers
        )
        print("\n[Test 6 – Update Obligation Status (Pending -> In Progress)]")
        print(f"  Status Code: {status_patch_resp.status_code}")
        print(f"  Response Body: {status_patch_resp.json()}")
        assert status_patch_resp.status_code == 200
        assert status_patch_resp.json()["status"] == "In Progress"

        # Test 7 – Complete Obligation (POST /obligations/{obligation_id}/complete)
        complete_resp = await client.post(
            f"/obligations/{ob1_id}/complete",
            headers=headers
        )
        print("\n[Test 7 – Complete Obligation]")
        print(f"  Status Code: {complete_resp.status_code}")
        print(f"  Response Body: {complete_resp.json()}")
        assert complete_resp.status_code == 200
        completed_ob = complete_resp.json()
        assert completed_ob["status"] == "Completed"
        assert completed_ob["completion_date"] == str(date.today())

        # Test 10 – Overdue Obligation Detection
        past_due = str(date.today() - timedelta(days=5))
        overdue_ob_resp = await client.post(
            "/obligations",
            json={
                "contract_id": contract_id,
                "title": "Overdue Annual Audit",
                "description": "Annual compliance audit due 5 days ago",
                "obligation_type": "Legal Compliance Requirement",
                "due_date": past_due,
                "assigned_to": user_id
            },
            headers=headers
        )
        print("\n[Test 10 – Overdue Obligation Detection]")
        print(f"  Status Code: {overdue_ob_resp.status_code}")
        print(f"  Response Body: {overdue_ob_resp.json()}")
        assert overdue_ob_resp.status_code == 201
        assert overdue_ob_resp.json()["status"] == "Overdue"

        # Test 8 – Non-existing Obligation (GET /obligations/999999)
        not_found_ob = await client.get("/obligations/999999", headers=headers)
        print("\n[Test 8 – Non-existing Obligation ID]")
        print(f"  Status Code: {not_found_ob.status_code}")
        print(f"  Response Body: {not_found_ob.json()}")
        assert not_found_ob.status_code == 404

        # Test 11 - Invalid Assigned User
        invalid_user_ob = await client.post(
            "/obligations",
            json={
                "contract_id": contract_id,
                "title": "Invalid Assigned User Test",
                "obligation_type": "Payment Obligation",
                "assigned_to": 999999
            },
            headers=headers
        )
        print("\n[Test 11 – Invalid Assigned User ID]")
        print(f"  Status Code: {invalid_user_ob.status_code}")
        print(f"  Response Body: {invalid_user_ob.json()}")
        assert invalid_user_ob.status_code == 404

        print("\n==================================================")
        print("[SUCCESS] ALL SPRINT 9 OBLIGATION TESTS PASSED 100% SUCCESSFULLY!")
        print("==================================================")


if __name__ == "__main__":
    asyncio.run(test_sprint9_obligations())
