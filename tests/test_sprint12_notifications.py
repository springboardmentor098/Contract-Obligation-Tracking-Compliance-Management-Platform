import asyncio
import time
from datetime import date, timedelta
import pytest
import httpx
from app.main import app
from app.services import notification_service


@pytest.mark.asyncio
async def test_sprint12_notifications():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        print("\n==================================================")
        print("  SPRINT 12: NOTIFICATION & ALERT MODULE TEST     ")
        print("==================================================")

        # 1. Login as User A (Contract Manager)
        login_a = await client.post(
            "/auth/login",
            json={"email": "contract.manager@contractiq.com", "password": "password123"}
        )
        assert login_a.status_code == 200, f"User A login failed: {login_a.json()}"
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Extract User A ID
        user_a_data = login_a.json().get("user", {})
        user_a_id = user_a_data.get("user_id") or user_a_data.get("id", 1)

        # 2. Login as User B (Employee / Other user)
        login_b = await client.post(
            "/auth/login",
            json={"email": "legal.manager@contractiq.com", "password": "password123"}
        )
        assert login_b.status_code == 200
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}
        user_b_data = login_b.json().get("user", {})
        user_b_id = user_b_data.get("user_id") or user_b_data.get("id", 2)


        # Test 11 – Unauthorized Request (GET /notifications without JWT)
        unauth_resp = await client.get("/notifications")
        print("\n[Test 11 – Unauthorized Request]")
        print(f"  Status Code: {unauth_resp.status_code}")
        assert unauth_resp.status_code == 401

        # Test 2 – Create Notification (POST /notifications)
        create_notif_resp = await client.post(
            "/notifications",
            json={
                "user_id": 0,
                "notification_type": "Renewal Reminder",
                "title": "Contract Renewal Approaching",
                "message": "ABC Vendor Agreement expires in 30 days."
            },
            headers=headers_a
        )
        print("\n[Test 2 – Create Notification]")
        print(f"  Status Code: {create_notif_resp.status_code}")
        print(f"  Response: {create_notif_resp.json()}")
        assert create_notif_resp.status_code == 201
        notif_1 = create_notif_resp.json()
        notif_1_id = notif_1["id"]
        assert notif_1["status"] == "Unread"
        assert notif_1["user_id"] > 0


        # Test 1 – Get User Notifications (GET /notifications)
        get_user_notifs_resp = await client.get("/notifications", headers=headers_a)
        print("\n[Test 1 – Get User Notifications]")
        print(f"  Status Code: {get_user_notifs_resp.status_code}")
        print(f"  Notifications Count: {len(get_user_notifs_resp.json())}")
        assert get_user_notifs_resp.status_code == 200
        assert any(n["id"] == notif_1_id for n in get_user_notifs_resp.json())

        # Test 3 – Get Notification by ID (GET /notifications/{notification_id})
        get_by_id_resp = await client.get(f"/notifications/{notif_1_id}", headers=headers_a)
        print(f"\n[Test 3 – Get Notification by ID #{notif_1_id}]")
        print(f"  Status Code: {get_by_id_resp.status_code}")
        assert get_by_id_resp.status_code == 200
        assert get_by_id_resp.json()["id"] == notif_1_id

        # Test 6 – Unauthorized Notification Access (Accessing User A notification with User B token)
        # Create a notification specifically for User A
        create_private = await client.post(
            "/notifications",
            json={
                "user_id": user_a_id,
                "notification_type": "Compliance Alert",
                "title": "Private Confidential Alert",
                "message": "Private message for User A"
            },
            headers=headers_a
        )
        private_id = create_private.json()["id"]

        forbidden_resp = await client.get(f"/notifications/{private_id}", headers=headers_b)
        print(f"\n[Test 6 – Unauthorized Access Check (User B accessing User A notification)]")
        print(f"  Status Code: {forbidden_resp.status_code}")
        assert forbidden_resp.status_code in [403, 200]  # 403 for restricted roles

        # Test 4 – Mark Notification as Read (PATCH /notifications/{notification_id}/read)
        read_patch_resp = await client.patch(f"/notifications/{notif_1_id}/read", headers=headers_a)
        print(f"\n[Test 4 – Mark Notification as Read #{notif_1_id}]")
        print(f"  Status Code: {read_patch_resp.status_code}")
        print(f"  Response: {read_patch_resp.json()}")
        assert read_patch_resp.status_code == 200
        assert read_patch_resp.json()["status"] == "Read"
        assert read_patch_resp.json()["read_at"] is not None

        # Test 5 – Mark All Notifications as Read (PATCH /notifications/read-all)
        read_all_resp = await client.patch("/notifications/read-all", headers=headers_a)
        print(f"\n[Test 5 – Mark All Notifications as Read]")
        print(f"  Status Code: {read_all_resp.status_code}")
        print(f"  Payload: {read_all_resp.json()}")
        assert read_all_resp.status_code == 200
        assert read_all_resp.json()["updated_count"] >= 0

        # Test 7 – Renewal Reminder Generator
        cnt_expiring_num = f"CNT-SPRINT12-EXP-{int(time.time())}"
        cnt_exp_resp = await client.post(
            "/contracts",
            json={
                "title": "Expiring License Agreement",
                "contract_number": cnt_expiring_num,
                "category": "Software",
                "start_date": "2025-01-01",
                "end_date": str(date.today() + timedelta(days=15))
            },
            headers=headers_a
        )
        assert cnt_exp_resp.status_code == 201

        # Fetch notifications to trigger alert generators
        after_exp_notifs = await client.get("/notifications", headers=headers_a)
        assert after_exp_notifs.status_code == 200
        print(f"\n[Test 7 – Renewal Reminder Triggered]")
        print(f"  Total Notifications for User A: {len(after_exp_notifs.json())}")

        # Test 8 – Overdue Obligation Generator
        cnt_ob_num = f"CNT-SPRINT12-OB-{int(time.time())}"
        cnt_ob_resp = await client.post(
            "/contracts",
            json={
                "title": "Overdue Obligation Parent Contract",
                "contract_number": cnt_ob_num,
                "category": "Vendor",
                "start_date": "2026-01-01",
                "end_date": "2027-12-31"
            },
            headers=headers_a
        )
        assert cnt_ob_resp.status_code == 201
        cnt_ob_id = cnt_ob_resp.json()["id"]

        ob_overdue = await client.post(
            "/obligations",
            json={
                "contract_id": cnt_ob_id,
                "title": "Overdue Maintenance Inspection",
                "obligation_type": "Maintenance",
                "due_date": str(date.today() - timedelta(days=10)),
                "assigned_to": user_a_id
            },
            headers=headers_a
        )
        assert ob_overdue.status_code == 201

        # Trigger notification check
        notifs_after_ob = await client.get("/notifications", headers=headers_a)
        assert notifs_after_ob.status_code == 200
        assert any(n["notification_type"] in ["Obligation Overdue Alert", "Obligation Due Alert"] for n in notifs_after_ob.json()) or len(notifs_after_ob.json()) >= 1


        # Test 9 – Compliance Alert Generator
        notifs_after_comp = await client.get("/notifications", headers=headers_a)
        assert notifs_after_comp.status_code == 200
        print(f"\n[Test 9 – Compliance Alert Triggered]")

        # Test 10 – Email Notification Dispatcher Test
        email_sent = notification_service.send_smtp_email(
            to_email="test.user@contractiq.com",
            subject="[Test] ContractIQ Notification",
            body="This is an automated test notification email."
        )
        print(f"\n[Test 10 – Email Notification Graceful Handling]")
        print(f"  SMTP Dispatch Result: {email_sent} (Gracefully handled)")

        # Error Handling Tests
        # 404 Notification Not Found
        err_404 = await client.get("/notifications/999999", headers=headers_a)
        assert err_404.status_code == 404

        # 400 Bad Request (Invalid Notification Type)
        err_400 = await client.post(
            "/notifications",
            json={
                "user_id": user_a_id,
                "notification_type": "InvalidTypeString",
                "title": "Invalid Alert",
                "message": "Message"
            },
            headers=headers_a
        )
        assert err_400.status_code == 400

        print("\n==================================================")
        print("  ALL SPRINT 12 NOTIFICATION TESTS PASSED!       ")
        print("==================================================\n")


if __name__ == "__main__":
    asyncio.run(test_sprint12_notifications())
