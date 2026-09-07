export type UserRole =
  | 'Administrator' | 'Legal Manager' | 'Compliance Officer'
  | 'Contract Manager' | 'Department Head' | 'Employee';

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export type ContractCategory =
  | 'Employment Contract' | 'Vendor Contract' | 'Service Agreement' | 'Lease Agreement'
  | 'Purchase Agreement' | 'Partnership Agreement' | 'Confidentiality Agreement';

export type ContractStatus = 'Draft' | 'Under Review' | 'Approved' | 'Active' | 'Expired' | 'Terminated';

export interface ContractListItem {
  id: number;
  title: string;
  contract_number: string;
  category: ContractCategory;
  status: ContractStatus;
  end_date: string;
}

export interface Contract extends ContractListItem {
  description?: string | null;
  start_date: string;
  created_by: number;
  assigned_to?: number | null;
  reviewed_at?: string | null;
  approved_at?: string | null;
  activated_at?: string | null;
  created_at: string;
  updated_at: string;
}

export type ObligationType =
  | 'Payment Obligation' | 'Delivery Commitment' | 'Reporting Requirement'
  | 'Renewal Condition' | 'Service Level Agreement' | 'Legal Compliance Requirement';

export type ObligationStatus = 'Pending' | 'In Progress' | 'Completed' | 'Delayed' | 'Overdue';

export interface ObligationListItem {
  id: number;
  contract_id: number;
  title: string;
  obligation_type: ObligationType;
  due_date: string;
  status: ObligationStatus;
}

export interface Obligation extends ObligationListItem {
  description?: string | null;
  assigned_to?: number | null;
  completion_date?: string | null;
  created_at: string;
  updated_at: string;
}

export type RenewalStatus = 'Upcoming' | 'In Progress' | 'Renewed' | 'Expired' | 'Cancelled';

export interface Renewal {
  id: number;
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  status: RenewalStatus;
  assigned_to?: number | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export type ComplianceStatus = 'Compliant' | 'Pending' | 'Delayed' | 'Non-Compliant' | 'High Risk';
export type RiskLevel = 'Low' | 'Medium' | 'High';

export interface ContractCompliance {
  contract_id: number;
  contract_number: string;
  compliance_status: ComplianceStatus;
  compliance_score: number;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  in_progress_obligations: number;
  delayed_obligations: number;
  overdue_obligations: number;
  risk_level: RiskLevel;
  evaluated_at: string;
}

export interface ComplianceListItem {
  contract_id: number;
  contract_number: string;
  compliance_status: ComplianceStatus;
  compliance_score: number;
}

export interface ComplianceSummary {
  total_contracts: number;
  compliant_contracts: number;
  pending_contracts: number;
  delayed_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
}

export interface HighRiskContract {
  contract_id: number;
  contract_number: string;
  risk_level: RiskLevel;
  overdue_obligations: number;
}

export interface NonCompliantContract {
  contract_id: number;
  contract_number: string;
  compliance_status: ComplianceStatus;
  overdue_obligations: number;
}

export type NotificationType =
  | 'Renewal Reminder' | 'Obligation Due Alert' | 'Obligation Overdue Alert'
  | 'Compliance Alert' | 'Contract Approval Alert' | 'Contract Status Alert';

export interface AppNotification {
  id: number;
  user_id: number;
  contract_id?: number | null;
  obligation_id?: number | null;
  notification_type: NotificationType;
  title: string;
  message: string;
  status: 'Unread' | 'Read';
  scheduled_at?: string | null;
  sent_at?: string | null;
  read_at?: string | null;
  created_at: string;
}

export interface DashboardSummary {
  contracts: any;
  obligations: any;
  renewals: any;
  compliance: any;
}
