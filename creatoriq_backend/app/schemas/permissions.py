from enum import Enum


class Role(str, Enum):
    ADMINISTRATOR = "Administrator"
    LEGAL_MANAGER = "Legal Manager"
    COMPLIANCE_OFFICER = "Compliance Officer"
    CONTRACT_MANAGER = "Contract Manager"
    DEPARTMENT_HEAD = "Department Head"
    EMPLOYEE = "Employee"


class Permission(str, Enum):
    MANAGE_USERS = "manage_users"
    MANAGE_CONTRACTS = "manage_contracts"
    MANAGE_OBLIGATIONS = "manage_obligations"
    MANAGE_RENEWALS = "manage_renewals"
    VIEW_REPORTS = "view_reports"
    MANAGE_REPORTS = "manage_reports"
    VIEW_AUDIT_LOGS = "view_audit_logs"


ROLE_PERMISSIONS = {
    Role.ADMINISTRATOR: {
        Permission.MANAGE_USERS,
        Permission.MANAGE_CONTRACTS,
        Permission.MANAGE_OBLIGATIONS,
        Permission.MANAGE_RENEWALS,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_REPORTS,
        Permission.VIEW_AUDIT_LOGS,
    },

    Role.LEGAL_MANAGER: {
        Permission.MANAGE_CONTRACTS,
        Permission.MANAGE_RENEWALS,
        Permission.VIEW_REPORTS,
    },

    Role.COMPLIANCE_OFFICER: {
        Permission.MANAGE_OBLIGATIONS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_AUDIT_LOGS,
    },

    Role.CONTRACT_MANAGER: {
        Permission.MANAGE_CONTRACTS,
        Permission.MANAGE_RENEWALS,
        Permission.VIEW_REPORTS,
    },

    Role.DEPARTMENT_HEAD: {
        Permission.MANAGE_OBLIGATIONS,
        Permission.VIEW_REPORTS,
    },

    Role.EMPLOYEE: {
        Permission.VIEW_REPORTS,
    },
}