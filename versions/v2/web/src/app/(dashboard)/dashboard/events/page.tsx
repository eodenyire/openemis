"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "lucide-react";
import { StatCard } from "@/components/shared/StatCard";

interface Event {
  id: number;
  name: string;
  start_date: string;
  end_date: string | null;
  location: string | null;
  event_type: string | null;
  max_participants: number | null;
  registered: number;
}

const cols: Column<Event>[] = [
  { key: "name", header: "Event" },
  { key: "event_type", header: "Type", render: (r) => r.event_type ?? "—" },
  { key: "start_date", header: "Date", render: (r) => new Date(r.start_date).toLocaleDateString() },
  { key: "location", header: "Location", render: (r) => r.location ?? "—" },
  { key: "registered", header: "Registered" },
  { key: "max_participants", header: "Capacity", render: (r) => r.max_participants ?? "Unlimited" },
];

export default function EventsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["events"],
    queryFn: () => api.get<{ total: number; items: Event[] }>("/events/").then(r => r.data),
  });

  const upcoming = data?.items.filter(e => new Date(e.start_date) >= new Date()).length ?? 0;

  return (
    <PageShell title="Events & Calendar" subtitle="School events and registrations">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Events" value={data?.total ?? "—"} icon={Calendar} />
        <StatCard title="Upcoming" value={upcoming} icon={Calendar} />
        <StatCard title="Total Registered" value={data?.items.reduce((s, e) => s + e.registered, 0) ?? "—"} icon={Calendar} />
      </div>
      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id" emptyMessage="No events found." />
    </PageShell>
  );
}
