from enum import Enum


class UserRole(str, Enum):
    ADMINISTRATOR = "Administrator"
    LEGAL_MANAGER = "Legal Manager"
    COMPLIANCE_OFFICER = "Compliance Officer"
    CONTRACT_MANAGER = "Contract Manager"
    DEPARTMENT_HEAD = "Department Head"
    EMPLOYEE = "Employee"


ROLE_PERMISSIONS = {
    UserRole.ADMINISTRATOR: {
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "contracts:read",
        "contracts:create",
        "contracts:update",
        "contracts:delete",
        "obligations:read",
        "obligations:create",
        "obligations:update",
        "reports:read",
        "audit_logs:read",
    },

    UserRole.LEGAL_MANAGER: {
        "users:read",
        "contracts:read",
        "contracts:create",
        "contracts:update",
        "obligations:read",
        "reports:read",
    },

    UserRole.COMPLIANCE_OFFICER: {
        "users:read",
        "contracts:read",
        "obligations:read",
        "obligations:create",
        "obligations:update",
        "reports:read",
        "audit_logs:read",
    },

    UserRole.CONTRACT_MANAGER: {
        "users:read",
        "contracts:read",
        "contracts:create",
        "contracts:update",
        "obligations:read",
        "renewals:read",
        "renewals:create",
    },

    UserRole.DEPARTMENT_HEAD: {
        "users:read",
        "contracts:read",
        "obligations:read",
        "reports:read",
    },

    UserRole.EMPLOYEE: {
        "contracts:read",
        "obligations:read",
    },
}