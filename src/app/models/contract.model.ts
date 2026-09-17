export interface Contract {
  id: number;
  title: string;
  contract_number: string;
  category: string;
  description: string | null;
  start_date: string;
  end_date: string | null;
  status: string;
  created_by: number;
  assigned_to: number | null;
  reviewed_at: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CreateContractRequest {
  title: string;
  contract_number: string;
  category: string;
  description: string;
  start_date: string;
  end_date: string;
}

export interface UpdateContractRequest {
  title: string;
  category: string;
  description: string;
  start_date: string;
  end_date: string;
}

export interface UpdateContractStatusRequest {
  status: string;
}