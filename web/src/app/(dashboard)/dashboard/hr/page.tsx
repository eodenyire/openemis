"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Users, UserCheck } from "lucide-react";

interface Staff { id: number; employee_id: string; first_name: string; last_name: string; designation: string; department: string | null; employment_type: string; active: boolean; }
interface Leave { id: number; staff_name: string; leave_type: string; start_date: string; end_date: string; status: string; days: number; }
interface Payslip { id: number; staff_name: string; period: string; gross_pay: number; net_pay: number; status: string; }

const staffCols: Column<Staff>[] = [
  { key: "employee_id", header: "Employee ID" },
  { key: "first_name", header: "First Name" },
  { key: "last_name", header: "Last Name" },
  { key: "designation", header: "Designation" },
  { key: "department", header: "Department", render: (r) => r.department ?? "—" },
  { key: "employment_type", header: "Type" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

const leaveCols: Column<Leave>[] = [
  { key: "staff_name", header: "Staff" },
  { key: "leave_type", header: "Type" },
  { key: "start_date", header: "From" },
  { key: "end_date", header: "To" },
  { key: "days", header: "Days" },
  { key: "status", header: "Status", render: (r) => <Badge variant={r.status === "approved" ? "default" : r.status === "rejected" ? "destructive" : "secondary"}>{r.status}</Badge> },
];

const payslipCols: Column<Payslip>[] = [
  { key: "staff_name", header: "Staff" },
  { key: "period", header: "Period" },
  { key: "gross_pay", header: "Gross", render: (r) => `KES ${Number(r.gross_pay).toLocaleString()}` },
  { key: "net_pay", header: "Net", render: (r) => `KES ${Number(r.net_pay).toLocaleString()}` },
  { key: "status", header: "Status", render: (r) => <Badge variant={r.status === "paid" ? "default" : "secondary"}>{r.status}</Badge> },
];

export default function HRPage() {
  const { data: staff, isLoading: loadingStaff } = useQuery({
    queryKey: ["hr-staff"],
    queryFn: () => api.get<{ total: number; items: Staff[] }>("/hr/staff/").then((r) => r.data),
  });

  const { data: leaves, isLoading: loadingLeaves } = useQuery({
    queryKey: ["leave-requests"],
    queryFn: () => api.get<{ total: number; items: Leave[] }>("/leave/requests/?limit=100").then((r) => r.data),
  });

  const { data: payslips, isLoading: loadingPayslips } = useQuery({
    queryKey: ["payslips"],
    queryFn: () => api.get<{ total: number; items: Payslip[] }>("/payroll/payslips/?limit=100").then((r) => r.data),
  });

  const active = staff?.items.filter((s) => s.active).length ?? 0;

  return (
    <PageShell title="Human Resources" subtitle="Staff management, leave and payroll"
      reports={[
        { label: "Staff Directory", endpoint: "/reports/staff/directory/excel", filename: "staff-directory.xlsx" },
        { label: "Payroll Report", endpoint: "/reports/staff/payroll/excel", filename: "payroll.xlsx" },
      ]}
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Staff" value={staff?.total ?? "—"} icon={Users} />
        <StatCard title="Active" value={active} icon={UserCheck} />
        <StatCard title="Pending Leave" value={leaves?.items.filter((l) => l.status === "pending").length ?? "—"} icon={Users} />
      </div>

      <Tabs defaultValue="staff">
        <TabsList>
          <TabsTrigger value="staff">Staff</TabsTrigger>
          <TabsTrigger value="leave">Leave Requests</TabsTrigger>
          <TabsTrigger value="payroll">Payroll</TabsTrigger>
        </TabsList>
        <TabsContent value="staff" className="mt-4">
          <DataTable columns={staffCols} data={staff?.items ?? []} loading={loadingStaff} keyField="id" emptyMessage="No staff found." />
        </TabsContent>
        <TabsContent value="leave" className="mt-4">
          <DataTable columns={leaveCols} data={leaves?.items ?? []} loading={loadingLeaves} keyField="id" emptyMessage="No leave requests." />
        </TabsContent>
        <TabsContent value="payroll" className="mt-4">
          <DataTable columns={payslipCols} data={payslips?.items ?? []} loading={loadingPayslips} keyField="id" emptyMessage="No payslips found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
