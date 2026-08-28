import asyncio
import time
from datetime import date, timedelta
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_sprint11_compliance():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        print("\n==================================================")
        print("  SPRINT 11: COMPLIANCE MONITORING & RISK TEST   ")
        print("==================================================")

        # 1. Login as Compliance Officer / Contract Manager to get authentication token
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

        # Test 8 – Unauthorized Request (GET /compliance without JWT)
        unauth_resp = await client.get("/compliance")
        print("\n[Test 8 – Unauthorized Request]")
        print(f"  Status Code: {unauth_resp.status_code}")
        assert unauth_resp.status_code == 401

        # 2. Setup Test Data 1: Fully Compliant Contract
        cnt_num_comp = f"CNT-SPRINT11-COMP-{int(time.time())}"
        contract_comp_resp = await client.post(
            "/contracts",
            json={
                "title": "Compliant SLA Agreement",
                "contract_number": cnt_num_comp,
                "category": "Service Agreement",
                "description": "100% Compliant test contract",
                "start_date": "2026-01-01",
                "end_date": "2027-12-31"
            },
            headers=headers
        )
        assert contract_comp_resp.status_code == 201
        comp_contract_id = contract_comp_resp.json()["id"]

        # Add 2 Completed Obligations to Contract A
        for i in range(1, 3):
            ob_resp = await client.post(
                "/obligations",
                json={
                    "contract_id": comp_contract_id,
                    "title": f"Completed Obligation #{i}",
                    "obligation_type": "Audit",
                    "due_date": str(date.today() - timedelta(days=5)),
                    "assigned_to": user_id
                },
                headers=headers
            )
            assert ob_resp.status_code == 201
            ob_id = ob_resp.json()["id"]
            # Mark obligation as Completed
            status_update = await client.patch(
                f"/obligations/{ob_id}/status",
                json={"status": "Completed"},
                headers=headers
            )
            assert status_update.status_code == 200

        # 3. Setup Test Data 2: High Risk / Non-Compliant Contract
        cnt_num_risk = f"CNT-SPRINT11-RISK-{int(time.time())}"
        contract_risk_resp = await client.post(
            "/contracts",
            json={
                "title": "High Risk Vendor Contract",
                "contract_number": cnt_num_risk,
                "category": "Vendor Agreement",
                "description": "High risk test contract with overdue obligations",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31"
            },
            headers=headers
        )
        assert contract_risk_resp.status_code == 201
        risk_contract_id = contract_risk_resp.json()["id"]

        # Add 2 Overdue Obligations to Contract B
        for i in range(1, 3):
            await client.post(
                "/obligations",
                json={
                    "contract_id": risk_contract_id,
                    "title": f"Overdue Obligation #{i}",
                    "obligation_type": "Payment",
                    "due_date": str(date.today() - timedelta(days=15)),
                    "assigned_to": user_id
                },
                headers=headers
            )

        # Test 1 & 6 – Get Contract Compliance (Fully Compliant)
        comp_eval_resp = await client.get(f"/contracts/{comp_contract_id}/compliance", headers=headers)
        print("\n[Test 1 & 6 – Contract Compliance Evaluation (Compliant Contract)]")
        print(f"  Status Code: {comp_eval_resp.status_code}")
        print(f"  Payload: {comp_eval_resp.json()}")
        assert comp_eval_resp.status_code == 200
        comp_data = comp_eval_resp.json()
        assert comp_data["compliance_status"] == "Compliant"
        assert comp_data["compliance_score"] == 100.0
        assert comp_data["risk_level"] == "Low"

        # Test 1 & 7 – Get Contract Compliance (High Risk Contract)
        risk_eval_resp = await client.get(f"/contracts/{risk_contract_id}/compliance", headers=headers)
        print("\n[Test 1 & 7 – Contract Compliance Evaluation (High Risk Contract)]")
        print(f"  Status Code: {risk_eval_resp.status_code}")
        print(f"  Payload: {risk_eval_resp.json()}")
        assert risk_eval_resp.status_code == 200
        risk_data = risk_eval_resp.json()
        assert risk_data["compliance_status"] == "High Risk"
        assert risk_data["risk_level"] == "High"
        assert risk_data["overdue_obligations"] == 2

        # Test 2 – Compliance Summary (GET /compliance/summary)
        summary_resp = await client.get("/compliance/summary", headers=headers)
        print("\n[Test 2 – Compliance Dashboard Summary]")
        print(f"  Status Code: {summary_resp.status_code}")
        print(f"  Summary Payload: {summary_resp.json()}")
        assert summary_resp.status_code == 200
        sum_data = summary_resp.json()
        assert sum_data["total_contracts"] >= 2
        assert sum_data["compliant_contracts"] >= 1
        assert sum_data["high_risk_contracts"] >= 1

        # Test 3 – All Compliance Records (GET /compliance)
        all_comp_resp = await client.get("/compliance", headers=headers)
        print("\n[Test 3 – Get All Compliance Records]")
        print(f"  Status Code: {all_comp_resp.status_code}")
        print(f"  Count: {len(all_comp_resp.json())}")
        assert all_comp_resp.status_code == 200
        assert any(c["contract_id"] == comp_contract_id for c in all_comp_resp.json())

        # Test 4 – Non-Compliant Contracts (GET /compliance/non-compliant)
        non_comp_resp = await client.get("/compliance/non-compliant", headers=headers)
        print("\n[Test 4 – Get Non-Compliant Contracts]")
        print(f"  Status Code: {non_comp_resp.status_code}")
        print(f"  Count: {len(non_comp_resp.json())}")
        assert non_comp_resp.status_code == 200
        assert any(c["contract_id"] == risk_contract_id for c in non_comp_resp.json())

        # Test 5 – High-Risk Contracts (GET /compliance/high-risk)
        high_risk_resp = await client.get("/compliance/high-risk", headers=headers)
        print("\n[Test 5 – Get High-Risk Contracts]")
        print(f"  Status Code: {high_risk_resp.status_code}")
        print(f"  Count: {len(high_risk_resp.json())}")
        assert high_risk_resp.status_code == 200
        assert any(c["contract_id"] == risk_contract_id for c in high_risk_resp.json())

        # Audit History Test (GET /contracts/{contract_id}/compliance/history)
        history_resp = await client.get(f"/contracts/{risk_contract_id}/compliance/history", headers=headers)
        print(f"\n[Audit History Test – Contract #{risk_contract_id}]")
        print(f"  Status Code: {history_resp.status_code}")
        print(f"  History Entries Count: {len(history_resp.json())}")
        assert history_resp.status_code == 200
        assert len(history_resp.json()) >= 1

        # Error Handling Test – 404 Contract Not Found
        err_resp = await client.get("/contracts/999999/compliance", headers=headers)
        print(f"\n[Error Handling Test – 404 Contract Not Found]")
        print(f"  Status Code: {err_resp.status_code}")
        assert err_resp.status_code == 404

        print("\n==================================================")
        print("  ALL SPRINT 11 COMPLIANCE TESTS PASSED!         ")
        print("==================================================\n")


if __name__ == "__main__":
    asyncio.run(test_sprint11_compliance())
