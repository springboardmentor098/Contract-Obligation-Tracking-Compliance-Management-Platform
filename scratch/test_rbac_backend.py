import json
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.activity import Activity
from app.core.rbac_seed import ensure_default_rbac_users

# Ensure seed users are present
ensure_default_rbac_users()

client = TestClient(app)

CREDENTIALS = {
    "Admin": ("admin@contractiq.com", "Admin@123"),
    "Legal Manager": ("legal@contractiq.com", "Legal@123"),
    "Contract Manager": ("contract@contractiq.com", "Contract@123"),
    "Compliance Officer": ("compliance@contractiq.com", "Compliance@123"),
    "Viewer": ("viewer@contractiq.com", "Viewer@123"),
}

tokens = {}

print("--- 1. Testing Default User Logins & JWT Generation ---")
for role_name, (email, password) in CREDENTIALS.items():
    res = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200, f"Failed login for {email}: {res.text}"
    data = res.json()
    assert "access_token" in data, f"No token for {email}"
    tokens[role_name] = data["access_token"]
    print(f"[OK] {role_name} ({email}) logged in successfully. Token generated.")

def auth_header(role_name):
    return {"Authorization": f"Bearer {tokens[role_name]}"}

print("\n--- 2. Testing RBAC Enforcement (403 Forbidden) ---")

# A. Contract Creation
# Allowed: Admin, Legal Manager, Contract Manager
# Denied (403): Compliance Officer, Viewer
test_contract_payload = {
    "title": "RBAC Test Contract",
    "contract_number": "RBAC-TEST-001",
    "category": "Vendor",
    "description": "Testing permissions",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "department": "Legal",
}

# Viewer attempt to create contract -> Must be 403
res = client.post("/contracts", json=test_contract_payload, headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on POST /contracts, got {res.status_code}: {res.text}"
print("[OK] Viewer blocked from POST /contracts with 403 Forbidden")

# Compliance Officer attempt to create contract -> Must be 403
res = client.post("/contracts", json=test_contract_payload, headers=auth_header("Compliance Officer"))
assert res.status_code == 403, f"Expected 403 for Compliance Officer on POST /contracts, got {res.status_code}: {res.text}"
print("[OK] Compliance Officer blocked from POST /contracts with 403 Forbidden")

# B. Contract Deletion
# Denied (403): Contract Manager, Compliance Officer, Viewer
res = client.delete("/contracts/99999", headers=auth_header("Contract Manager"))
assert res.status_code == 403, f"Expected 403 for Contract Manager on DELETE /contracts, got {res.status_code}"
print("[OK] Contract Manager blocked from DELETE /contracts with 403 Forbidden")

res = client.delete("/contracts/99999", headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on DELETE /contracts, got {res.status_code}"
print("[OK] Viewer blocked from DELETE /contracts with 403 Forbidden")

# C. User Management
# Denied (403): Legal Manager, Contract Manager, Compliance Officer, Viewer
for role in ["Legal Manager", "Contract Manager", "Compliance Officer", "Viewer"]:
    res = client.get("/users", headers=auth_header(role))
    assert res.status_code == 403, f"Expected 403 for {role} on GET /users, got {res.status_code}"
    print(f"[OK] {role} blocked from GET /users with 403 Forbidden")

    res = client.post("/users", json={"full_name": "Test", "email": "x@x.com", "password": "123", "role": "Viewer"}, headers=auth_header(role))
    assert res.status_code == 403, f"Expected 403 for {role} on POST /users, got {res.status_code}"
    print(f"[OK] {role} blocked from POST /users with 403 Forbidden")

# Admin allowed to GET /users
res = client.get("/users", headers=auth_header("Admin"))
assert res.status_code == 200, f"Admin failed GET /users: {res.status_code}"
print("[OK] Admin successfully accessed GET /users (200 OK)")

# D. Obligations & Renewals
# Denied (403): Viewer
res = client.get("/obligations", headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on GET /obligations, got {res.status_code}"
print("[OK] Viewer blocked from GET /obligations with 403 Forbidden")

res = client.get("/renewals", headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on GET /renewals, got {res.status_code}"
print("[OK] Viewer blocked from GET /renewals with 403 Forbidden")

# E. Compliance Module
# Denied (403): Contract Manager, Viewer
res = client.get("/compliance", headers=auth_header("Contract Manager"))
assert res.status_code == 403, f"Expected 403 for Contract Manager on GET /compliance, got {res.status_code}"
print("[OK] Contract Manager blocked from GET /compliance with 403 Forbidden")

res = client.get("/compliance", headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on GET /compliance, got {res.status_code}"
print("[OK] Viewer blocked from GET /compliance with 403 Forbidden")

# F. Activity Logs
# Denied (403): Contract Manager, Viewer
res = client.get("/activities/", headers=auth_header("Contract Manager"))
assert res.status_code == 403, f"Expected 403 for Contract Manager on GET /activities/, got {res.status_code}"
print("[OK] Contract Manager blocked from GET /activities/ with 403 Forbidden")

res = client.get("/activities/", headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on GET /activities/, got {res.status_code}"
print("[OK] Viewer blocked from GET /activities/ with 403 Forbidden")

# Allowed: Compliance Officer
res = client.get("/activities/", headers=auth_header("Compliance Officer"))
assert res.status_code == 200, f"Expected 200 for Compliance Officer on GET /activities/, got {res.status_code}"
print("[OK] Compliance Officer successfully accessed GET /activities/ (200 OK)")

# G. Reports
# Denied (403): Contract Manager
res = client.get("/reports", headers=auth_header("Contract Manager"))
assert res.status_code == 403, f"Expected 403 for Contract Manager on GET /reports, got {res.status_code}"
print("[OK] Contract Manager blocked from GET /reports with 403 Forbidden")

# Viewer allowed GET /reports (view only)
res = client.get("/reports", headers=auth_header("Viewer"))
assert res.status_code == 200, f"Expected 200 for Viewer on GET /reports, got {res.status_code}"
print("[OK] Viewer successfully accessed GET /reports (view-only 200 OK)")

# Viewer blocked from POST /reports (generating)
res = client.post("/reports", json={"report_name": "Test", "report_type": "Executive Summary"}, headers=auth_header("Viewer"))
assert res.status_code == 403, f"Expected 403 for Viewer on POST /reports, got {res.status_code}"
print("[OK] Viewer blocked from POST /reports with 403 Forbidden")

# H. Role Change Activity Logging
print("\n--- 3. Testing Role Change Activity Logging ---")
# Create a temporary user with Admin
temp_res = client.post("/users", json={"full_name": "Role Change Test", "email": "temp_role_test@contractiq.com", "password": "Password@123", "role": "Viewer"}, headers=auth_header("Admin"))
if temp_res.status_code == 201:
    temp_user = temp_res.json()
    temp_id = temp_user["id"]
    # Change role to "Legal Manager"
    patch_res = client.put(f"/users/{temp_id}", json={"role": "Legal Manager"}, headers=auth_header("Admin"))
    assert patch_res.status_code == 200, f"Failed updating user role: {patch_res.text}"
    print(f"[OK] Admin changed user role to Legal Manager")

    # Check database activity log
    db = SessionLocal()
    role_change_log = db.query(Activity).filter(Activity.action == "ROLE_CHANGE", Activity.entity_id == temp_id).first()
    assert role_change_log is not None, "ROLE_CHANGE activity log not found in database!"
    print(f"[OK] ROLE_CHANGE activity logged in PostgreSQL: '{role_change_log.description}'")

    # Clean up temp user
    del_res = client.delete(f"/users/{temp_id}", headers=auth_header("Admin"))
    assert del_res.status_code == 200
    db.close()
    print("[OK] Temp user deleted and cleaned up")

print("\n=======================================================")
print("ALL BACKEND RBAC TESTS PASSED FLAWLESSLY!")
print("=======================================================")
