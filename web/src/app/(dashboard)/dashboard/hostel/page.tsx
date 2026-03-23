"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Building2, BedDouble, Users } from "lucide-react";

interface Block { id: number; name: string; gender: string | null; }
interface Room { id: number; name: string; capacity: number; state: string; block_id: number | null; }
interface Allocation { id: number; student_id: number; room_id: number; check_in_date: string; check_out_date: string | null; state: string; monthly_fee: number | null; }

const blockCols: Column<Block>[] = [
  { key: "name", header: "Block Name" },
  { key: "gender", header: "Gender", render: (r) => r.gender ?? "Mixed" },
];

const roomCols: Column<Room>[] = [
  { key: "name", header: "Room" },
  { key: "capacity", header: "Capacity" },
  { key: "state", header: "Status", render: (r) => <Badge variant={r.state === "available" ? "default" : r.state === "occupied" ? "secondary" : "destructive"}>{r.state}</Badge> },
];

const allocCols: Column<Allocation>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "room_id", header: "Room ID" },
  { key: "check_in_date", header: "Check-in" },
  { key: "check_out_date", header: "Check-out", render: (r) => r.check_out_date ?? "—" },
  { key: "monthly_fee", header: "Monthly Fee", render: (r) => r.monthly_fee ? `KES ${r.monthly_fee}` : "—" },
  { key: "state", header: "Status", render: (r) => <Badge variant={r.state === "confirmed" ? "default" : "secondary"}>{r.state}</Badge> },
];

export default function HostelPage() {
  const { data: summary } = useQuery({ queryKey: ["hostel-summary"], queryFn: () => api.get<any>("/hostel/summary").then(r => r.data) });
  const { data: blocks, isLoading: loadingBlocks } = useQuery({ queryKey: ["hostel-blocks"], queryFn: () => api.get<Block[]>("/hostel/blocks/").then(r => r.data) });
  const { data: rooms, isLoading: loadingRooms } = useQuery({ queryKey: ["hostel-rooms"], queryFn: () => api.get<Room[]>("/hostel/rooms/").then(r => r.data) });
  const { data: allocs, isLoading: loadingAllocs } = useQuery({ queryKey: ["hostel-allocs"], queryFn: () => api.get<Allocation[]>("/hostel/allocations/").then(r => r.data) });

  return (
    <PageShell title="Hostel" subtitle="Blocks, rooms and student allocations">
      <div className="grid gap-4 sm:grid-cols-4">
        <StatCard title="Total Rooms" value={summary?.total_rooms ?? "—"} icon={BedDouble} />
        <StatCard title="Total Capacity" value={summary?.total_capacity ?? "—"} icon={Building2} />
        <StatCard title="Occupied" value={summary?.occupied ?? "—"} icon={Users} />
        <StatCard title="Occupancy Rate" value={summary ? `${summary.occupancy_rate}%` : "—"} icon={Building2} />
      </div>

      <Tabs defaultValue="blocks">
        <TabsList>
          <TabsTrigger value="blocks">Blocks</TabsTrigger>
          <TabsTrigger value="rooms">Rooms</TabsTrigger>
          <TabsTrigger value="allocations">Allocations</TabsTrigger>
        </TabsList>
        <TabsContent value="blocks" className="mt-4">
          <DataTable columns={blockCols} data={blocks ?? []} loading={loadingBlocks} keyField="id" emptyMessage="No blocks found." />
        </TabsContent>
        <TabsContent value="rooms" className="mt-4">
          <DataTable columns={roomCols} data={rooms ?? []} loading={loadingRooms} keyField="id" emptyMessage="No rooms found." />
        </TabsContent>
        <TabsContent value="allocations" className="mt-4">
          <DataTable columns={allocCols} data={allocs ?? []} loading={loadingAllocs} keyField="id" emptyMessage="No allocations found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
