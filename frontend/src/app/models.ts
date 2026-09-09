export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: string;
}

export interface DashboardSummary {
  contracts: { total: number; active: number; draft: number; under_review: number; approved: number; expired: number; terminated: number; by_category: Record<string, number> };
  obligations: { total: number; pending: number; in_progress: number; completed: number; delayed: number; overdue: number };
  renewals: { upcoming: number; in_progress: number; renewed: number; expired: number; cancelled: number; approaching_expiry: Array<{ contract_id: number; contract_number: string; contract_title: string; expiry_date: string; days_remaining: number }> };
  compliance: { total_contracts: number; compliant: number; pending: number; delayed: number; non_compliant: number; high_risk: number; average_score: number };
}