from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def get_admin_headers():
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@contractiq.com",
            "password": "Admin@12345",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_dashboard_summary():
    headers = get_admin_headers()

    response = client.get(
        "/dashboard/summary",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "contracts" in data
    assert "obligations" in data
    assert "renewals" in data
    assert "compliance" in data

    assert data["contracts"]["total"] >= 0
    assert data["obligations"]["total"] >= 0
    assert data["renewals"]["total"] >= 0


def test_contract_analytics():
    headers = get_admin_headers()

    response = client.get(
        "/reports/analytics/contracts",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()["contracts"]

    assert "total" in data
    assert "by_status" in data
    assert "by_category" in data
    assert "by_counterparty" in data
    assert "expiring_next_30_days" in data
    assert "expiring_next_90_days" in data


def test_obligation_analytics():
    headers = get_admin_headers()

    response = client.get(
        "/reports/analytics/obligations",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()["obligations"]

    assert "total" in data
    assert "by_status" in data
    assert "by_priority" in data
    assert "by_responsible_party" in data
    assert "overdue" in data
    assert "due_next_7_days" in data
    assert "due_next_30_days" in data


def test_renewal_analytics():
    headers = get_admin_headers()

    response = client.get(
        "/reports/analytics/renewals",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()["renewals"]

    assert "total" in data
    assert "by_status" in data
    assert "due_next_7_days" in data
    assert "due_next_30_days" in data
    assert "due_next_90_days" in data
    assert "overdue" in data
    assert "by_contract" in data


def test_compliance_analytics():
    headers = get_admin_headers()

    response = client.get(
        "/reports/analytics/compliance",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()["compliance"]

    assert "total_contracts" in data
    assert "compliant_contracts" in data
    assert "non_compliant_contracts" in data
    assert "high_risk_contracts" in data
    assert "compliance_rate" in data
    assert "overdue_obligations" in data
    assert "high_priority_overdue_obligations" in data


def test_export_contract_excel():
    headers = get_admin_headers()

    response = client.get(
        "/reports/export/contracts/excel",
        headers=headers,
    )

    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(response.content) > 0


def test_export_contract_pdf():
    headers = get_admin_headers()

    response = client.get(
        "/reports/export/contracts/pdf",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_export_obligation_excel():
    headers = get_admin_headers()

    response = client.get(
        "/reports/export/obligations/excel",
        headers=headers,
    )

    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(response.content) > 0


def test_export_renewal_excel():
    headers = get_admin_headers()

    response = client.get(
        "/reports/export/renewals/excel",
        headers=headers,
    )

    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(response.content) > 0


def test_export_dashboard_pdf():
    headers = get_admin_headers()

    response = client.get(
        "/reports/export/dashboard/pdf",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_analytics_requires_authentication():
    endpoints = [
        "/dashboard/summary",
        "/reports/analytics/contracts",
        "/reports/analytics/obligations",
        "/reports/analytics/renewals",
        "/reports/analytics/compliance",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_exports_require_authentication():
    endpoints = [
        "/reports/export/contracts/excel",
        "/reports/export/contracts/pdf",
        "/reports/export/obligations/excel",
        "/reports/export/renewals/excel",
        "/reports/export/dashboard/pdf",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401
