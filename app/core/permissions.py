from enum import Enum


class Permission(str, Enum):
    # -----------------------------
    # Contract permissions
    # -----------------------------
    CREATE_CONTRACT = "create_contract"
    READ_CONTRACT = "read_contract"
    UPDATE_CONTRACT = "update_contract"
    DELETE_CONTRACT = "delete_contract"

    SUBMIT_FOR_REVIEW = "submit_for_review"
    APPROVE_CONTRACT = "approve_contract"
    ACTIVATE_CONTRACT = "activate_contract"
    EXPIRE_CONTRACT = "expire_contract"

    ASSIGN_CONTRACT = "assign_contract"

    # -----------------------------
    # Obligation permissions
    # -----------------------------
    CREATE_OBLIGATION = "create_obligation"
    READ_OBLIGATION = "read_obligation"
    UPDATE_OBLIGATION = "update_obligation"
    DELETE_OBLIGATION = "delete_obligation"

    # -----------------------------
    # Audit log permissions
    # -----------------------------
    READ_AUDIT_LOG = "read_audit_log"

    # -----------------------------
    # User management permissions
    # -----------------------------
    MANAGE_USERS = "manage_users"
    READ_USERS = "read_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"


ROLE_PERMISSIONS = {

    # =====================================================
    # ADMINISTRATOR
    # =====================================================

    "Administrator": {
        Permission.CREATE_CONTRACT,
        Permission.READ_CONTRACT,
        Permission.UPDATE_CONTRACT,
        Permission.DELETE_CONTRACT,

        Permission.CREATE_OBLIGATION,
        Permission.READ_OBLIGATION,
        Permission.UPDATE_OBLIGATION,
        Permission.DELETE_OBLIGATION,

        Permission.READ_AUDIT_LOG,

        Permission.SUBMIT_FOR_REVIEW,
        Permission.APPROVE_CONTRACT,
        Permission.ACTIVATE_CONTRACT,
        Permission.EXPIRE_CONTRACT,
        Permission.ASSIGN_CONTRACT,

        Permission.MANAGE_USERS,
        Permission.READ_USERS,
        Permission.UPDATE_USERS,
        Permission.DELETE_USERS,
    },

    # =====================================================
    # LEGAL MANAGER
    # =====================================================

    "Legal Manager": {
        Permission.CREATE_CONTRACT,
        Permission.READ_CONTRACT,
        Permission.UPDATE_CONTRACT,
        Permission.DELETE_CONTRACT,

        Permission.CREATE_OBLIGATION,
        Permission.READ_OBLIGATION,
        Permission.UPDATE_OBLIGATION,

        Permission.SUBMIT_FOR_REVIEW,
        Permission.APPROVE_CONTRACT,
        Permission.ASSIGN_CONTRACT,

        Permission.READ_USERS,
    },

    # =====================================================
    # COMPLIANCE OFFICER
    # =====================================================

    "Compliance Officer": {
        Permission.READ_CONTRACT,
        Permission.APPROVE_CONTRACT,

        Permission.READ_OBLIGATION,
        Permission.UPDATE_OBLIGATION,

        Permission.READ_AUDIT_LOG,
    },

    # =====================================================
    # CONTRACT MANAGER
    # =====================================================

    "Contract Manager": {
        Permission.CREATE_CONTRACT,
        Permission.READ_CONTRACT,
        Permission.UPDATE_CONTRACT,
        Permission.DELETE_CONTRACT,

        Permission.CREATE_OBLIGATION,
        Permission.READ_OBLIGATION,
        Permission.UPDATE_OBLIGATION,

        Permission.SUBMIT_FOR_REVIEW,
        Permission.ACTIVATE_CONTRACT,
        Permission.EXPIRE_CONTRACT,
        Permission.ASSIGN_CONTRACT,

        Permission.READ_USERS,
    },

    # =====================================================
    # DEPARTMENT HEAD
    # =====================================================

    "Department Head": {
        Permission.READ_CONTRACT,
        Permission.APPROVE_CONTRACT,

        Permission.READ_OBLIGATION,
    },

    # =====================================================
    # EMPLOYEE
    # =====================================================

    "Employee": {
        Permission.READ_CONTRACT,

        Permission.READ_OBLIGATION,
    },
}


def has_permission(
    role: str,
    permission: Permission,
) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())