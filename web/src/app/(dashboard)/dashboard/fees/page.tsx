"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { Badge } from "@/components/ui/badge";
import { DollarSign, TrendingUp, AlertCircle, Receipt } from "lucide-react";
import type { FinanceSummary } from "@/types";

interface Invoice {
  id: number;
  student_id: number;
  total_amount: number;
  paid_amount: number;
  due_date: string;
  state: string;
  student?: { first_name: string; last_name: string; admission_number: string };
}

const columns: Column<Invoice>[] = [
  { key: "id", header: "Invoice #" },
  {
    key: "student",
    header: "Student",
    render: (r) => r.student ? `${r.student.first_name} ${r.student.last_name}` : `Student #${r.student_id}`,
  },
  { key: "total_amount", header: "Invoiced", render: (r) => `KES ${Number(r.total_amount).toLocaleString()}` },
  { key: "paid_amount", header: "Paid", render: (r) => `KES ${Number(r.paid_amount).toLocaleString()}` },
  {
    key: "balance",
    header: "Balance",
    render: (r) => `KES ${(Number(r.total_amount) - Number(r.paid_amount)).toLocaleString()}`,
  },
  { key: "due_date", header: "Due Date" },
  {
    key: "state",
    header: "Status",
    render: (r) => (
      <Badge variant={r.state === "paid" ? "default" : r.state === "partial" ? "secondary" : "destructive"}>
        {r.state}
      </Badge>
    ),
  },
];

export default function FeesPage() {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ["finance-summary"],
    queryFn: () => api.get<FinanceSummary>("/finance/summary").then((r) => r.data),
  });

  const { data: invoices, isLoading: loadingInvoices } = useQuery({
    queryKey: ["fee-invoices"],
    queryFn: () => api.get<{ items: Invoice[]; total: number }>("/fees/invoices/").then((r) => r.data),
  });

  const { data: overdue } = useQuery({
    queryKey: ["overdue-invoices"],
    queryFn: () => api.get<Invoice[]>("/finance/invoices/overdue").then((r) => r.data),
  });

  return (
    <PageShell
      title="Fees"
      subtitle="Fee collection overview"
      reports={[
        { label: "Collection Report", endpoint: "/reports/finance/fee-collection/excel", filename: "fee-collection.xlsx" },
        { label: "Outstanding", endpoint: "/reports/finance/outstanding/excel", filename: "outstanding-fees.xlsx" },
      ]}
    >
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Invoiced"
          value={summary ? `KES ${Number(summary.total_invoiced_kes).toLocaleString()}` : "—"}
          icon={DollarSign} loading={loadingSummary}
        />
        <StatCard
          title="Total Collected"
          value={summary ? `KES ${Number(summary.total_collected_kes).toLocaleString()}` : "—"}
          icon={TrendingUp} loading={loadingSummary}
        />
        <StatCard
          title="Outstanding"
          value={summary ? `KES ${Number(summary.outstanding_kes).toLocaleString()}` : "—"}
          icon={AlertCircle} loading={loadingSummary}
        />
        <StatCard
          title="Collection Rate"
          value={summary ? `${summary.collection_rate_pct.toFixed(1)}%` : "—"}
          icon={Receipt} loading={loadingSummary}
        />
      </div>

      {overdue && overdue.length > 0 && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
          {overdue.length} overdue invoice{overdue.length !== 1 ? "s" : ""} require attention.
        </div>
      )}

      <DataTable
        columns={columns}
        data={invoices?.items ?? []}
        loading={loadingInvoices}
        keyField="id"
        emptyMessage="No fee invoices found."
      />
    </PageShell>
  );
}
