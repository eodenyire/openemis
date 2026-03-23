"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatCard } from "@/components/shared/StatCard";
import { Database } from "lucide-react";

interface NemisStudent { id: number; admission_number: string; first_name: string; last_name: string; nemis_upi: string | null; sync_status: string | null; }

const cols: Column<NemisStudent>[] = [
  { key: "admission_number", header: "Adm No" },
  { key: "first_name", header: "First Name" },
  { key: "last_name", header: "Last Name" },
  { key: "nemis_upi", header: "NEMIS UPI", render: (r) => r.nemis_upi ?? <Badge variant="destructive">Missing</Badge> },
  { key: "sync_status", header: "Sync", render: (r) => <Badge variant={r.sync_status === "synced" ? "default" : "secondary"}>{r.sync_status ?? "pending"}</Badge> },
];

export default function NemisPage() {
  const { data: stats } = useQuery({ queryKey: ["nemis-stats"], queryFn: () => api.get<any>("/nemis/stats").then(r => r.data) });
  const { data: students, isLoading } = useQuery({ queryKey: ["nemis-students"], queryFn: () => api.get<any>("/nemis/students").then(r => r.data) });

  const items: NemisStudent[] = Array.isArray(students) ? students : (students?.items ?? []);

  return (
    <PageShell title="NEMIS" subtitle="National Education Management Information System integration">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Students" value={stats?.total_students ?? "—"} icon={Database} />
        <StatCard title="With UPI" value={stats?.with_upi ?? "—"} icon={Database} />
        <StatCard title="Missing UPI" value={stats?.missing_upi ?? "—"} icon={Database} />
      </div>
      <DataTable columns={cols} data={items} loading={isLoading} keyField="id" emptyMessage="No NEMIS data found." />
    </PageShell>
  );
}
