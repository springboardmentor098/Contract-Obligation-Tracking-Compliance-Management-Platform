export const ROLES = {
  ADMIN: "Admin",
  LEGAL_MANAGER: "Legal Manager",
  CONTRACT_MANAGER: "Contract Manager",
  COMPLIANCE_OFFICER: "Compliance Officer",
  VIEWER: "Viewer",
} as const;

export type RoleType = typeof ROLES[keyof typeof ROLES] | "Administrator";

/**
 * Normalizes any role string to standard role representation.
 * Handles "Administrator" -> "Admin", case insensitivity, and trimming.
 */
export function normalizeRole(role?: string | null): string {
  if (!role) return "";
  const cleaned = role.trim().toLowerCase();
  if (cleaned === "admin" || cleaned === "administrator") return ROLES.ADMIN;
  if (cleaned === "legal manager") return ROLES.LEGAL_MANAGER;
  if (cleaned === "contract manager") return ROLES.CONTRACT_MANAGER;
  if (cleaned === "compliance officer") return ROLES.COMPLIANCE_OFFICER;
  if (cleaned === "viewer" || cleaned === "employee") return ROLES.VIEWER;
  return role.trim();
}

export function isAdmin(role?: string | null): boolean {
  return normalizeRole(role) === ROLES.ADMIN;
}

export function hasAnyRole(userRole: string | undefined | null, allowedRoles: string[]): boolean {
  const normUser = normalizeRole(userRole);
  return allowedRoles.some((r) => normalizeRole(r) === normUser);
}

/**
 * Checks whether a given role is authorized to view a particular frontend route path.
 */
export function canAccessRoute(pathname: string, userRole?: string | null): boolean {
  const role = normalizeRole(userRole);

  // Admin has full unrestricted access
  if (role === ROLES.ADMIN) return true;

  const path = pathname.toLowerCase();

  // Public/shared routes
  if (path === "/" || path === "/dashboard" || path.startsWith("/profile")) {
    return true;
  }

  // User management and Settings: Admin only
  if (path.startsWith("/users") || path.startsWith("/settings")) {
    return false;
  }

  // Viewer: Can only access Dashboard, Contracts (read-only), Reports (view-only), and Profile
  if (role === ROLES.VIEWER) {
    if (path.startsWith("/contracts")) return true;
    if (path.startsWith("/reports")) return true;
    return false;
  }

  // Contract Manager: Cannot access Reports, Compliance, Activity Logs, Settings, User Management
  if (role === ROLES.CONTRACT_MANAGER) {
    if (
      path.startsWith("/reports") ||
      path.startsWith("/compliance") ||
      path.startsWith("/activities")
    ) {
      return false;
    }
    return true; // contracts, obligations, renewals, notifications
  }

  // Compliance Officer: Can access Compliance, Obligations, Renewals, Reports, Notifications, Activities, Contracts (read-only)
  if (role === ROLES.COMPLIANCE_OFFICER) {
    return true;
  }

  // Legal Manager: Can access Contracts, Obligations, Renewals, Reports, Notifications, Activities (No User Mgmt or Settings)
  if (role === ROLES.LEGAL_MANAGER) {
    return true;
  }

  return false;
}

// -------------------------------------------------------------
// Action-level permission checkers
// -------------------------------------------------------------

export function canCreateContract(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER || r === ROLES.CONTRACT_MANAGER;
}

export function canEditContract(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER || r === ROLES.CONTRACT_MANAGER;
}

export function canDeleteContract(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER;
}

export function canApproveContract(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER;
}

export function canSubmitContractReview(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER || r === ROLES.CONTRACT_MANAGER;
}

export function canGenerateReport(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER || r === ROLES.COMPLIANCE_OFFICER;
}

export function canDeleteReport(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r === ROLES.ADMIN || r === ROLES.LEGAL_MANAGER;
}

export function canManageUsers(role?: string | null): boolean {
  return normalizeRole(role) === ROLES.ADMIN;
}

export function canAccessSettings(role?: string | null): boolean {
  return normalizeRole(role) === ROLES.ADMIN;
}

export function canManageNotifications(role?: string | null): boolean {
  const r = normalizeRole(role);
  return r !== ROLES.VIEWER;
}
