from app.core.permissions import Permission, has_permission


def test_employee_contract_permissions():
    assert has_permission("Employee", Permission.READ_CONTRACT) is True
    assert has_permission("Employee", Permission.CREATE_CONTRACT) is False
    assert has_permission("Employee", Permission.DELETE_CONTRACT) is False


def test_employee_audit_permission():
    assert has_permission("Employee", Permission.READ_AUDIT_LOG) is False


def test_administrator_contract_permissions():
    assert has_permission("Administrator", Permission.CREATE_CONTRACT) is True
    assert has_permission("Administrator", Permission.DELETE_CONTRACT) is True


def test_compliance_audit_permission():
    assert has_permission(
        "Compliance Officer",
        Permission.READ_AUDIT_LOG,
    ) is True
