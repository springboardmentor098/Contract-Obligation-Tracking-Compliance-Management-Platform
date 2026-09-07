from app.core.roles import UserRole


ROLE_PERMISSIONS = {
    UserRole.ADMINISTRATOR: {
        "users",
        "contracts",
        "contract_versions",
        "obligations",
        "renewals",
        "notifications",
        "reports",
        "activities",
        "audit_logs",
    },

    UserRole.LEGAL_MANAGER: {
        "contracts",
        "contract_versions",
        "obligations",
    },

    UserRole.COMPLIANCE_OFFICER: {
        "obligations",
        "renewals",
        "notifications",
        "reports",
    },

    UserRole.CONTRACT_MANAGER: {
        "contracts",
        "contract_versions",
        "renewals",
    },

    UserRole.DEPARTMENT_HEAD: {
        "contracts",
        "obligations",
        "reports",
    },

    UserRole.EMPLOYEE: {
        "contracts",
        "obligations",
    },
}