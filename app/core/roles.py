from enum import Enum


class UserRole(str, Enum):
    ADMINISTRATOR = "Administrator"
    LEGAL_MANAGER = "Legal Manager"
    COMPLIANCE_OFFICER = "Compliance Officer"
    CONTRACT_MANAGER = "Contract Manager"
    DEPARTMENT_HEAD = "Department Head"
    EMPLOYEE = "Employee"


ROLE_ALIASES = {
    "admin": UserRole.ADMINISTRATOR.value,
    "administrator": UserRole.ADMINISTRATOR.value,
    "legal manager": UserRole.LEGAL_MANAGER.value,
    "legalmanager": UserRole.LEGAL_MANAGER.value,
    "compliance officer": UserRole.COMPLIANCE_OFFICER.value,
    "complianceofficer": UserRole.COMPLIANCE_OFFICER.value,
    "contract manager": UserRole.CONTRACT_MANAGER.value,
    "contractmanager": UserRole.CONTRACT_MANAGER.value,
    "manager": UserRole.CONTRACT_MANAGER.value,
    "department head": UserRole.DEPARTMENT_HEAD.value,
    "departmenthead": UserRole.DEPARTMENT_HEAD.value,
    "employee": UserRole.EMPLOYEE.value,
    "analyst": UserRole.EMPLOYEE.value,
}


def normalize_role(role_name: str) -> str:
    """Normalize user role string to official ContractIQ user role name."""
    if not role_name:
        return UserRole.EMPLOYEE.value

    cleaned = role_name.strip().lower()
    if cleaned in ROLE_ALIASES:
        return ROLE_ALIASES[cleaned]

    for enum_role in UserRole:
        if enum_role.value.lower() in cleaned or cleaned in enum_role.value.lower():
            return enum_role.value

    return UserRole.EMPLOYEE.value
