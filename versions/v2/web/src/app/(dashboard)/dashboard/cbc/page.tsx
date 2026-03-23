"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatCard } from "@/components/shared/StatCard";
import { BookOpen } from "lucide-react";

interface GradeLevel { id: number; name: string; order: number; is_active: boolean; }
interface LearningArea { id: number; name: string; code: string | null; }

const gradeCols: Column<GradeLevel>[] = [
  { key: "order", header: "Order" },
  { key: "name", header: "Grade Level" },
  { key: "is_active", header: "Status", render: (r) => <Badge variant={r.is_active ? "default" : "secondary"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
];

export default function CbcPage() {
  const { data: grades, isLoading } = useQuery({
    queryKey: ["cbc-grades"],
    queryFn: () => api.get<GradeLevel[]>("/cbc/grade-levels").then(r => r.data),
  });

  const active = grades?.filter(g => g.is_active).length ?? 0;

  return (
    <PageShell title="CBC Curriculum" subtitle="Grade levels, learning areas and report cards">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Grade Levels" value={grades?.length ?? "—"} icon={BookOpen} />
        <StatCard title="Active Grades" value={active} icon={BookOpen} />
        <StatCard title="Inactive" value={(grades?.length ?? 0) - active} icon={BookOpen} />
      </div>

      <Tabs defaultValue="grades">
        <TabsList>
          <TabsTrigger value="grades">Grade Levels</TabsTrigger>
        </TabsList>
        <TabsContent value="grades" className="mt-4">
          <DataTable columns={gradeCols} data={grades ?? []} loading={isLoading} keyField="id" emptyMessage="No grade levels found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
