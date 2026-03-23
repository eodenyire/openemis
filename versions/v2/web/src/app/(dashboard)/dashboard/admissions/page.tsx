"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/shared/StatCard";
import { Users } from "lucide-react";

interface Admission {
  id: number;
  application_number: string;
  name: string;
  first_name: string;
  last_name: string;
  state: string;
  application_date: string;
}

const stateVariant = (s: string) => {
  if (s === "admission") return "default";
  if (s === "reject") return "destructive";
  if (s === "confirm") return "secondary";
  return "outline";
};

const cols: Column<Admission>[] = [
  { key: "application_number", header: "App No" },
  { key: "name", header: "Name" },
  { key: "application_date", header: "Date", render: (r) => r.application_date ? new Date(r.application_date).toLocaleDateString() : "—" },
  { key: "state", header: "Status", render: (r) => <Badge variant={stateVariant(r.state)}>{r.state}</Badge> },
];

export default function AdmissionsPage() {
  const { data: all, isLoading } = useQuery({ queryKey: ["admissions"], queryFn: () => api.get<Admission[]>("/admissions/").then(r => r.data) });
  const { data: pending } = useQuery({ queryKey: ["admissions-pending"], queryFn: () => api.get<Admission[]>("/admissions/?state=draft").then(r => r.data) });
  const { data: confirmed } = useQuery({ queryKey: ["admissions-confirmed"], queryFn: () => api.get<Admission[]>("/admissions/?state=admission").then(r => r.data) });

  return (
    <PageShell title="Admissions" subtitle="Student admission applications and status">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Applications" value={all?.length ?? "—"} icon={Users} />
        <StatCard title="Pending" value={pending?.length ?? "—"} icon={Users} />
        <StatCard title="Admitted" value={confirmed?.length ?? "—"} icon={Users} />
      </div>
      <DataTable columns={cols} data={all ?? []} loading={isLoading} keyField="id" emptyMessage="No admissions found." />
    </PageShell>
  );
}
