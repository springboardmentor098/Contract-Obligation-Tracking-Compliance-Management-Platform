export interface ComplianceEvaluation {
  contract_id: number;
  compliance_status: string;
  compliance_score: number;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  delayed_obligations: number;
  overdue_obligations: number;
  risk_level: string;
  evaluated_at: string;
}

export interface ComplianceRecord {
  id: number;
  contract_id: number;
  status: string;
  compliance_score: number;
  risk_level: string;
  notes: string | null;
  evaluated_at: string;
  created_at: string;
  updated_at: string;
}