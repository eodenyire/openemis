"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Slot { id: number; course_id: number; subject_id: number; teacher_id: number; day_of_week: string; timing_id: number; is_active: boolean; }
interface CalEvent { id: number; title: string; event_type: string; start_date: string; end_date: string; is_school_wide: boolean; }

const slotCols: Column<Slot>[] = [
  { key: "day_of_week", header: "Day", render: (r) => r.day_of_week.charAt(0).toUpperCase() + r.day_of_week.slice(1) },
  { key: "timing_id", header: "Period" },
  { key: "course_id", header: "Class ID" },
  { key: "subject_id", header: "Subject ID" },
  { key: "teacher_id", header: "Teacher ID" },
  { key: "is_active", header: "Status", render: (r) => <Badge variant={r.is_active ? "default" : "secondary"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
];

const calCols: Column<CalEvent>[] = [
  { key: "title", header: "Event" },
  { key: "event_type", header: "Type" },
  { key: "start_date", header: "Start" },
  { key: "end_date", header: "End" },
  { key: "is_school_wide", header: "School-wide", render: (r) => <Badge variant={r.is_school_wide ? "default" : "secondary"}>{r.is_school_wide ? "Yes" : "No"}</Badge> },
];

export default function TimetablePage() {
  const { data: slots, isLoading: loadingSlots } = useQuery({
    queryKey: ["timetable-slots"],
    queryFn: () => api.get<Slot[]>("/timetable/slots").then(r => r.data),
  });
  const { data: calendar, isLoading: loadingCal } = useQuery({
    queryKey: ["timetable-calendar"],
    queryFn: () => api.get<CalEvent[]>("/timetable/calendar").then(r => r.data),
  });

  return (
    <PageShell title="Timetable" subtitle="Class schedules and academic calendar">
      <Tabs defaultValue="slots">
        <TabsList>
          <TabsTrigger value="slots">Timetable Slots ({slots?.length ?? 0})</TabsTrigger>
          <TabsTrigger value="calendar">Academic Calendar ({calendar?.length ?? 0})</TabsTrigger>
        </TabsList>
        <TabsContent value="slots" className="mt-4">
          <DataTable columns={slotCols} data={slots ?? []} loading={loadingSlots} keyField="id" emptyMessage="No timetable slots found." />
        </TabsContent>
        <TabsContent value="calendar" className="mt-4">
          <DataTable columns={calCols} data={calendar ?? []} loading={loadingCal} keyField="id" emptyMessage="No calendar events found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
