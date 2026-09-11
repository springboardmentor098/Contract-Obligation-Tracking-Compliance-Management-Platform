export interface User {
  id?: number | string;
  email: string;
  full_name?: string;
  name?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type?: string;
  user?: User;
}

export interface Contract {
  id: number | string;
  title: string;
  contract_number: string;
  category: string;
  status: string;
  start_date?: string;
  end_date?: string;
  created_at?: string;
  created_by?: number | string;
  assigned_to?: number | string;
}

export interface Obligation {
  id: number | string;
  contract_id: number | string;
  title: string;
  description?: string;
  obligation_type?: string;
  due_date?: string;
  status: string;
  assigned_to?: number | string;
  priority?: string;
}

export interface Renewal {
  id: number | string;
  contract_id: number | string;
  renewal_date?: string;
  previous_expiry_date?: string;
  new_expiry_date?: string;
  status: string;
}

export interface Notification {
  id: number | string;
  title?: string;
  message?: string;
  type?: string;
  is_read?: boolean;
  read?: boolean;
  created_at?: string;
  status?: string;
}

export interface ComplianceRecord {
  id: number | string;
  contract_id?: number | string;
  obligation_id?: number | string;
  status: string;
  risk_level?: string;
  description?: string;
  updated_at?: string;
}

export interface Activity {
  id?: number | string;
  user?: string;
  action?: string;
  entity?: string;
  entity_id?: number | string;
  timestamp?: string;
  created_at?: string;
  details?: string;
}

export interface DashboardSummary {
  total_contracts: number;
  active_contracts: number;
  expired_contracts: number;
  pending_obligations: number;
  overdue_obligations: number;
  upcoming_renewals: number;
  compliance_summary: Record<string, number>;
  contract_status_distribution: Record<string, number>;
  obligation_status_distribution: Record<string, number>;
}
