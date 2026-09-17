export interface Obligation {
  id: number;
  contract_id: number;
  title: string;
  description: string | null;
  obligation_type: string;
  due_date: string;
  assigned_to: number | null;
  status: string;
  completion_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateObligationRequest {
  contract_id: number;
  title: string;
  description: string;
  obligation_type: string;
  due_date: string;
  assigned_to: number | null;
}

export interface UpdateObligationRequest {
  title: string;
  description: string;
  obligation_type: string;
  due_date: string;
  assigned_to: number | null;
}

export interface UpdateObligationStatusRequest {
  status: string;
}