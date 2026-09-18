export enum UserRole {
  Administrator = 'Administrator',
  LegalManager = 'Legal Manager',
  ComplianceOfficer = 'Compliance Officer',
  ContractManager = 'Contract Manager',
  DepartmentHead = 'Department Head',
  Employee = 'Employee'
}

export const ALL_ROLES = [
  UserRole.Administrator,
  UserRole.LegalManager,
  UserRole.ComplianceOfficer,
  UserRole.ContractManager,
  UserRole.DepartmentHead,
  UserRole.Employee
];

export const ROLE_PERMISSIONS: Record<string, string[]> = {
  [UserRole.Administrator]: [
    'View Dashboard',
    'View Contracts',
    'Create Contracts',
    'Update Contracts',
    'Approve Contracts',
    'Delete Contracts',
    'Manage Obligations',
    'Manage Renewals',
    'Manage Compliance',
    'View Reports',
    'View Notifications',
    'View Activity History',
    'Manage Users'
  ],

  [UserRole.LegalManager]: [
    'View Dashboard',
    'View Contracts',
    'Create Contracts',
    'Update Contracts',
    'Approve Contracts',
    'Manage Obligations',
    'Manage Renewals',
    'View Compliance',
    'View Reports',
    'View Notifications',
    'View Activity History'
  ],

  [UserRole.ComplianceOfficer]: [
    'View Dashboard',
    'View Contracts',
    'View Compliance',
    'Manage Compliance',
    'View Reports',
    'View Notifications',
    'View Activity History'
  ],

  [UserRole.ContractManager]: [
    'View Dashboard',
    'View Contracts',
    'Create Contracts',
    'Update Contracts',
    'Approve Contracts',
    'Manage Obligations',
    'Manage Renewals',
    'View Compliance',
    'View Reports',
    'View Notifications',
    'View Activity History'
  ],

  [UserRole.DepartmentHead]: [
    'View Dashboard',
    'View Contracts',
    'Create Contracts',
    'Update Contracts',
    'Approve Contracts',
    'Manage Obligations',
    'Manage Renewals',
    'View Compliance',
    'View Reports',
    'View Notifications',
    'View Activity History'
  ],

  [UserRole.Employee]: [
    'View Dashboard',
    'View Contracts',
    'View Obligations',
    'View Notifications',
    'View Activity History'
  ]
};