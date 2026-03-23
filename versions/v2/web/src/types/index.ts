export type Role = "admin" | "teacher" | "parent" | "student";

export interface User {
  username: string;
  role: Role;
}

export interface Student {
  id: number;
  adm_no: string;
  full_name: string;
  grade: string;
  gender: string;
  nemis_upi: string;
  status: string;
}

export interface Staff {
  id: number;
  full_name: string;
  tsc_no: string;
  designation: string;
  subject: string;
  status: string;
}

export interface FeeInvoice {
  id: number;
  student_name: string;
  adm_no: string;
  term: string;
  amount_invoiced: number;
  amount_paid: number;
  balance: number;
  status: string;
}

export interface FinanceSummary {
  total_invoiced_kes: number;
  total_collected_kes: number;
  outstanding_kes: number;
  collection_rate_pct: number;
  total_invoices: number;
  paid_invoices: number;
  overdue_invoices: number;
}

export interface AttendanceRecord {
  id: number;
  student_name: string;
  adm_no: string;
  date: string;
  status: string;
  grade: string;
}

export interface ExamSession {
  id: number;
  name: string;
  term: string;
  year: number;
  start_date: string;
  end_date: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
