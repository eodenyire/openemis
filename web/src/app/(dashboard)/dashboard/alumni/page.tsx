"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { GraduationCap } from "lucide-react";
import { StatCard } from "@/components/shared/StatCard";

interface Alumni {
  id: number;
  student_id: number;
  graduation_year: number | null;
  current_institution: string | null;
  current_employer: string | null;
  email: string | null;
  phone: string | null;
  active: boolean;
}

const cols: Column<Alumni>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "graduation_year", header: "Grad Year", render: (r) => r.graduation_year ?? "—" },
  { key: "current_institution", header: "Institution", render: (r) => r.current_institution ?? "—" },
  { key: "current_employer", header: "Employer", render: (r) => r.current_employer ?? "—" },
  { key: "email", header: "Email", render: (r) => r.email ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

export default function AlumniPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["alumni"],
    queryFn: () => api.get<{ total: number; items: Alumni[] }>("/alumni/").then(r => r.data),
  });

  return (
    <PageShell title="Alumni" subtitle="Former students and their current status">
      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard title="Total Alumni" value={data?.total ?? "—"} icon={GraduationCap} />
        <StatCard title="Active Records" value={data?.items.filter(a => a.active).length ?? "—"} icon={GraduationCap} />
      </div>
      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id" emptyMessage="No alumni records found." />
    </PageShell>
  );
}
