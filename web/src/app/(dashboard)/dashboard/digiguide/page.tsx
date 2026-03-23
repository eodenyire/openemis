"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

interface Career { id: number; name: string; cluster: string | null; min_grade: string | null; description: string | null; active: boolean; }
interface Match { id: number; student_id: number; career_id: number; match_score: number | null; recommended: boolean; }

const careerCols: Column<Career>[] = [
  { key: "name", header: "Career" },
  { key: "cluster", header: "Cluster", render: (r) => r.cluster ?? "—" },
  { key: "min_grade", header: "Min Grade", render: (r) => r.min_grade ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

const matchCols: Column<Match>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "career_id", header: "Career ID" },
  { key: "match_score", header: "Score", render: (r) => r.match_score != null ? `${r.match_score}%` : "—" },
  { key: "recommended", header: "Recommended", render: (r) => <Badge variant={r.recommended ? "default" : "secondary"}>{r.recommended ? "Yes" : "No"}</Badge> },
];

export default function DigiGuidePage() {
  const { data: careers, isLoading: loadingCareers } = useQuery({
    queryKey: ["digiguide-careers"],
    queryFn: () => api.get<Career[]>("/digiguide/careers").then(r => r.data),
  });
  const { data: matches, isLoading: loadingMatches } = useQuery({
    queryKey: ["digiguide-matches"],
    queryFn: () => api.get<Match[]>("/digiguide/matches").then(r => r.data),
  });

  return (
    <PageShell title="DigiGuide" subtitle="Career guidance and student-career matching">
      <Tabs defaultValue="careers">
        <TabsList>
          <TabsTrigger value="careers">Careers ({careers?.length ?? 0})</TabsTrigger>
          <TabsTrigger value="matches">Matches ({matches?.length ?? 0})</TabsTrigger>
        </TabsList>
        <TabsContent value="careers" className="mt-4">
          <DataTable columns={careerCols} data={careers ?? []} loading={loadingCareers} keyField="id" emptyMessage="No careers found." />
        </TabsContent>
        <TabsContent value="matches" className="mt-4">
          <DataTable columns={matchCols} data={matches ?? []} loading={loadingMatches} keyField="id" emptyMessage="No matches found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
