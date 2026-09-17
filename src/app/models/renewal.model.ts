export interface Renewal {
  id: number;
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  status: string;
  assigned_to: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateRenewalRequest {
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  status: string;
  assigned_to: number | null;
  notes: string;
}

export interface UpdateRenewalRequest {
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  status: string;
  assigned_to: number | null;
  notes: string;
}

export interface UpdateRenewalStatusRequest {
  status: string;
}