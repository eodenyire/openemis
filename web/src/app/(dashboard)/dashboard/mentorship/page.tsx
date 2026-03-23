"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Mentor { id: number; teacher_id: number; specialization: string | null; max_mentees: number; active: boolean; }
interface Group { id: number; name: string; mentor_id: number; academic_year_id: number | null; active: boolean; }

const mentorCols: Column<Mentor>[] = [
  { key: "teacher_id", header: "Teacher ID" },
  { key: "specialization", header: "Specialization", render: (r) => r.specialization ?? "—" },
  { key: "max_mentees", header: "Max Mentees" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

const groupCols: Column<Group>[] = [
  { key: "name", header: "Group Name" },
  { key: "mentor_id", header: "Mentor ID" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

export default function MentorshipPage() {
  const { data: mentors, isLoading: loadingMentors } = useQuery({
    queryKey: ["mentors"],
    queryFn: () => api.get<Mentor[]>("/mentorship/mentors").then(r => r.data),
  });
  const { data: groups, isLoading: loadingGroups } = useQuery({
    queryKey: ["mentorship-groups"],
    queryFn: () => api.get<Group[]>("/mentorship/groups").then(r => r.data),
  });

  return (
    <PageShell title="Mentorship" subtitle="Mentors and mentorship groups">
      <Tabs defaultValue="mentors">
        <TabsList>
          <TabsTrigger value="mentors">Mentors ({mentors?.length ?? 0})</TabsTrigger>
          <TabsTrigger value="groups">Groups ({groups?.length ?? 0})</TabsTrigger>
        </TabsList>
        <TabsContent value="mentors" className="mt-4">
          <DataTable columns={mentorCols} data={mentors ?? []} loading={loadingMentors} keyField="id" emptyMessage="No mentors found." />
        </TabsContent>
        <TabsContent value="groups" className="mt-4">
          <DataTable columns={groupCols} data={groups ?? []} loading={loadingGroups} keyField="id" emptyMessage="No groups found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
