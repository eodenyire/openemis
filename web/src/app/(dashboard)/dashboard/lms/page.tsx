"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatCard } from "@/components/shared/StatCard";
import { BookOpen } from "lucide-react";

interface Classroom { id: number; name: string; course_id: number; subject_id: number; teacher_id: number; join_code: string | null; is_active: boolean; }

const cols: Column<Classroom>[] = [
  { key: "name", header: "Classroom" },
  { key: "course_id", header: "Course ID" },
  { key: "subject_id", header: "Subject ID" },
  { key: "teacher_id", header: "Teacher ID" },
  { key: "join_code", header: "Join Code", render: (r) => r.join_code ? <code className="bg-muted px-1 rounded text-xs">{r.join_code}</code> : "—" },
  { key: "is_active", header: "Status", render: (r) => <Badge variant={r.is_active ? "default" : "secondary"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
];

export default function LmsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["lms-classrooms"],
    queryFn: () => api.get<Classroom[]>("/lms/classrooms").then(r => r.data),
  });

  const active = data?.filter(c => c.is_active).length ?? 0;

  return (
    <PageShell title="LMS / Digital Classrooms" subtitle="Virtual classrooms, assignments and quizzes">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Classrooms" value={data?.length ?? "—"} icon={BookOpen} />
        <StatCard title="Active" value={active} icon={BookOpen} />
        <StatCard title="Inactive" value={(data?.length ?? 0) - active} icon={BookOpen} />
      </div>
      <DataTable columns={cols} data={data ?? []} loading={isLoading} keyField="id" emptyMessage="No classrooms found." />
    </PageShell>
  );
}
