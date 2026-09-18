export interface User {
  id: number;
  username?: string | null;
  email: string;
  full_name?: string | null;
  role: string;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
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

  description?: string;

  start_date?: string;

  end_date?: string;

  status: string;

  created_by?: number | string;

  assigned_to?: number | string | null;

  reviewed_at?: string;

  approved_at?: string;

  created_at?: string;

  updated_at?: string;

}

export interface Obligation {
  id: number | string;
  contract_id: number | string;
  title: string;
  description?: string;
  obligation_type?: string;
  due_date?: string;
  status: string;
  assigned_to?: number | string | null;
  priority?: string;
}

export interface Renewal {

  id: number;

  contract_id: number;

  renewal_date: string;

  previous_expiry_date: string;

  new_expiry_date: string;

  status:
    | 'Upcoming'
    | 'In Progress'
    | 'Renewed'
    | 'Expired'
    | 'Cancelled'
    | string;

  assigned_to?: number | null;

  notes?: string | null;

  created_at?: string;

  updated_at?: string;

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
  contract_id: number | string;
  contract_number: string;

  compliance_status: string;
  compliance_score: number;

  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  delayed_obligations: number;
  overdue_obligations: number;

  risk_level: string;
  evaluated_at?: string;
}

export interface Activity {

  id?: number | string;

  user_id?: number | string;

  user?: string;

  email?: string;

  role?: string;

  action?: string;

  action_text?: string;

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

