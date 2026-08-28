import asyncio
import time
from datetime import date, timedelta
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_sprint10_renewals():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        print("\n==================================================")
        print("  SPRINT 10: RENEWAL & EXPIRY MONITORING MODULE   ")
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

        # Fetch valid user ID
        users_resp = await client.get("/users", headers=headers)
        if users_resp.status_code == 200 and len(users_resp.json()) > 0:
            user_id = users_resp.json()[0].get("user_id") or users_resp.json()[0].get("id", 1)
        else:
            user_id = 1

        # 2. Create parent contracts for renewal tests
        cnt_num_1 = f"CNT-SPRINT10-A-{int(time.time())}"
        contract_1_resp = await client.post(
            "/contracts",
            json={
                "title": "ABC Vendor Agreement",
                "contract_number": cnt_num_1,
                "category": "Vendor Contract",
                "description": "Renewal management test contract",
                "start_date": "2026-08-01",
                "end_date": "2027-07-31"
            },
            headers=headers
        )
        assert contract_1_resp.status_code == 201, f"Contract 1 creation failed: {contract_1_resp.json()}"
        contract_1_id = contract_1_resp.json()["id"]

        # Test 10 – Unauthorized Request (POST /renewals without token)
        unauth_resp = await client.post(
            "/renewals",
            json={
                "contract_id": contract_1_id,
                "renewal_date": "2027-07-01",
                "previous_expiry_date": "2027-07-31",
                "new_expiry_date": "2028-07-31"
            }
        )
        print("\n[Test 10 – Unauthorized Request]")
        print(f"  Status Code: {unauth_resp.status_code}")
        assert unauth_resp.status_code == 401

        # Test 1 – Create Renewal (POST /renewals)
        create_ren_resp = await client.post(
            "/renewals",
            json={
                "contract_id": contract_1_id,
                "renewal_date": "2027-07-01",
                "previous_expiry_date": "2027-07-31",
                "new_expiry_date": "2028-07-31",
                "assigned_to": user_id,
                "notes": "Annual vendor agreement renewal"
            },
            headers=headers
        )
        print("\n[Test 1 – Create Renewal Record]")
        print(f"  Status Code: {create_ren_resp.status_code}")
        print(f"  Response Payload: {create_ren_resp.json()}")
        assert create_ren_resp.status_code == 201
        ren_1 = create_ren_resp.json()
        ren_1_id = ren_1["id"]
        assert ren_1["contract_id"] == contract_1_id
        assert ren_1["status"] == "Upcoming"
        assert ren_1["new_expiry_date"] == "2028-07-31"

        # Test 2 – Get All Renewals (GET /renewals)
        get_all_resp = await client.get("/renewals", headers=headers)
        print("\n[Test 2 – Get All Renewals]")
        print(f"  Status Code: {get_all_resp.status_code}")
        print(f"  Count: {len(get_all_resp.json())}")
        assert get_all_resp.status_code == 200
        assert any(r["id"] == ren_1_id for r in get_all_resp.json())

        # Test 3 – Get Renewal by ID (GET /renewals/{renewal_id})
        get_by_id_resp = await client.get(f"/renewals/{ren_1_id}", headers=headers)
        print(f"\n[Test 3 – Get Renewal by ID #{ren_1_id}]")
        print(f"  Status Code: {get_by_id_resp.status_code}")
        assert get_by_id_resp.status_code == 200
        assert get_by_id_resp.json()["id"] == ren_1_id

        # Test 4 – Get Renewals for a Contract (GET /contracts/{contract_id}/renewals)
        get_cnt_ren_resp = await client.get(f"/contracts/{contract_1_id}/renewals", headers=headers)
        print(f"\n[Test 4 – Get Renewals for Contract #{contract_1_id}]")
        print(f"  Status Code: {get_cnt_ren_resp.status_code}")
        print(f"  Contract Renewal History Count: {len(get_cnt_ren_resp.json())}")
        assert get_cnt_ren_resp.status_code == 200
        assert len(get_cnt_ren_resp.json()) >= 1

        # Test 5 – Update Renewal (PUT /renewals/{renewal_id})
        update_resp = await client.put(
            f"/renewals/{ren_1_id}",
            json={
                "notes": "Updated notes: Annual vendor agreement review in progress"
            },
            headers=headers
        )
        print(f"\n[Test 5 – Update Renewal #{ren_1_id}]")
        print(f"  Status Code: {update_resp.status_code}")
        assert update_resp.status_code == 200
        assert "review in progress" in update_resp.json()["notes"]

        # Test 6 – Update Renewal Status (PATCH /renewals/{renewal_id}/status: Upcoming -> In Progress)
        status_patch_resp = await client.patch(
            f"/renewals/{ren_1_id}/status",
            json={"status": "In Progress"},
            headers=headers
        )
        print(f"\n[Test 6 – Update Renewal Status (Upcoming -> In Progress)]")
        print(f"  Status Code: {status_patch_resp.status_code}")
        print(f"  Updated Status: {status_patch_resp.json().get('status')}")
        assert status_patch_resp.status_code == 200
        assert status_patch_resp.json()["status"] == "In Progress"

        # Invalid transition test (In Progress -> Upcoming should fail with 400)
        invalid_status_resp = await client.patch(
            f"/renewals/{ren_1_id}/status",
            json={"status": "Upcoming"},
            headers=headers
        )
        print(f"  Invalid Transition Check (In Progress -> Upcoming): Status {invalid_status_resp.status_code}")
        assert invalid_status_resp.status_code == 400

        # Test 7 – Complete Renewal (POST /renewals/{renewal_id}/renew)
        complete_resp = await client.post(
            f"/renewals/{ren_1_id}/renew",
            json={
                "new_expiry_date": "2028-07-31",
                "notes": "Renewal finalized and executed successfully."
            },
            headers=headers
        )
        print(f"\n[Test 7 – Complete Renewal #{ren_1_id}]")
        print(f"  Status Code: {complete_resp.status_code}")
        print(f"  Final Renewal Payload: {complete_resp.json()}")
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "Renewed"
        assert complete_resp.json()["new_expiry_date"] == "2028-07-31"

        # Verify contract end_date updated
        check_contract_resp = await client.get(f"/contracts/{contract_1_id}", headers=headers)
        assert check_contract_resp.status_code == 200
        assert check_contract_resp.json()["end_date"] == "2028-07-31"
        print(f"  Verified Contract #{contract_1_id} end_date updated to: {check_contract_resp.json()['end_date']}")

        # Test 8 – Upcoming Renewal Detection (GET /renewals/upcoming)
        # Create a contract expiring in 20 days
        upcoming_expiry = str(date.today() + timedelta(days=20))
        cnt_num_up = f"CNT-SPRINT10-UP-{int(time.time())}"
        contract_up_resp = await client.post(
            "/contracts",
            json={
                "title": "Software License Agreement",
                "contract_number": cnt_num_up,
                "category": "Software",
                "start_date": str(date.today() - timedelta(days=340)),
                "end_date": upcoming_expiry
            },
            headers=headers
        )
        assert contract_up_resp.status_code == 201
        contract_up_id = contract_up_resp.json()["id"]

        upcoming_detection_resp = await client.get("/renewals/upcoming?days=30", headers=headers)
        print(f"\n[Test 8 – Upcoming Renewal Detection (Threshold: 30 days)]")
        print(f"  Status Code: {upcoming_detection_resp.status_code}")
        print(f"  Detected Upcoming Contracts Count: {len(upcoming_detection_resp.json())}")
        assert upcoming_detection_resp.status_code == 200
        assert any(c["contract_id"] == contract_up_id for c in upcoming_detection_resp.json())

        # Test 9 – Expired Contract Detection (GET /renewals/expired)
        # Create a contract whose expiry date has passed 10 days ago
        expired_date = str(date.today() - timedelta(days=10))
        cnt_num_exp = f"CNT-SPRINT10-EXP-{int(time.time())}"
        contract_exp_resp = await client.post(
            "/contracts",
            json={
                "title": "Office Lease Agreement",
                "contract_number": cnt_num_exp,
                "category": "Real Estate",
                "start_date": "2025-01-01",
                "end_date": expired_date
            },
            headers=headers
        )
        assert contract_exp_resp.status_code == 201
        contract_exp_id = contract_exp_resp.json()["id"]

        expired_detection_resp = await client.get("/renewals/expired", headers=headers)
        print(f"\n[Test 9 – Expired Contract Detection]")
        print(f"  Status Code: {expired_detection_resp.status_code}")
        print(f"  Detected Expired Contracts Count: {len(expired_detection_resp.json())}")
        assert expired_detection_resp.status_code == 200
        assert any(c["contract_id"] == contract_exp_id for c in expired_detection_resp.json())

        # Additional Error Handling Tests (Section 20)
        # 404 Contract Not Found
        err_cnt_resp = await client.post(
            "/renewals",
            json={"contract_id": 999999, "new_expiry_date": "2028-12-31"},
            headers=headers
        )
        assert err_cnt_resp.status_code == 404

        # 404 Renewal Not Found
        err_ren_resp = await client.get("/renewals/999999", headers=headers)
        assert err_ren_resp.status_code == 404

        # 400 Invalid Date Range (new_expiry_date < previous_expiry_date)
        err_date_resp = await client.post(
            "/renewals",
            json={
                "contract_id": contract_1_id,
                "previous_expiry_date": "2028-07-31",
                "new_expiry_date": "2027-01-01"
            },
            headers=headers
        )
        assert err_date_resp.status_code == 400

        print("\n==================================================")
        print("  ALL SPRINT 10 RENEWAL TESTS PASSED SUCCESSFULLY! ")
        print("==================================================\n")


if __name__ == "__main__":
    asyncio.run(test_sprint10_renewals())
