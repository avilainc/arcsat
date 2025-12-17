export interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerCreate {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  status?: string;
}

export interface Deal {
  id: number;
  title: string;
  description?: string;
  value: number;
  stage: string;
  customer_id: number;
  probability: number;
  expected_close_date?: string;
  created_at: string;
  updated_at: string;
}

export interface DealCreate {
  title: string;
  description?: string;
  value: number;
  stage: string;
  customer_id: number;
  probability?: number;
  expected_close_date?: string;
}

export interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  customer_id: number;
  created_at: string;
}

export interface ContactCreate {
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  customer_id: number;
}

export interface Activity {
  id: number;
  title: string;
  description?: string;
  activity_type: string;
  status: string;
  customer_id: number;
  deal_id?: number;
  due_date?: string;
  created_at: string;
}

export interface ActivityCreate {
  title: string;
  description?: string;
  activity_type: string;
  status?: string;
  customer_id: number;
  deal_id?: number;
  due_date?: string;
}
