export interface Notification {

  id: number;

  user_id: number;

  contract_id: number | null;

  obligation_id: number | null;

  notification_type: string;

  title: string;

  message: string;

  status: string;

  scheduled_at: string | null;

  sent_at: string | null;

  read_at: string | null;

  created_at: string;

  updated_at: string;

}