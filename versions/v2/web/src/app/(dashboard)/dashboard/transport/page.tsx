"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bus, MapPin, Users } from "lucide-react";

interface Route { id: number; name: string; start_point: string | null; end_point: string | null; active: boolean; }
interface Vehicle { id: number; name: string; registration_number: string; capacity: number | null; driver_name: string | null; active: boolean; }

const routeCols: Column<Route>[] = [
  { key: "name", header: "Route" },
  { key: "start_point", header: "From", render: (r) => r.start_point ?? "—" },
  { key: "end_point", header: "To", render: (r) => r.end_point ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

const vehicleCols: Column<Vehicle>[] = [
  { key: "name", header: "Vehicle" },
  { key: "registration_number", header: "Reg No" },
  { key: "capacity", header: "Capacity", render: (r) => r.capacity ?? "—" },
  { key: "driver_name", header: "Driver", render: (r) => r.driver_name ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

export default function TransportPage() {
  const { data: summary } = useQuery({ queryKey: ["transport-summary"], queryFn: () => api.get<any>("/transport/summary").then(r => r.data) });
  const { data: routes, isLoading: loadingRoutes } = useQuery({ queryKey: ["transport-routes"], queryFn: () => api.get<Route[]>("/transport/routes/").then(r => r.data) });
  const { data: vehicles, isLoading: loadingVehicles } = useQuery({ queryKey: ["transport-vehicles"], queryFn: () => api.get<Vehicle[]>("/transport/vehicles/").then(r => r.data) });

  return (
    <PageShell title="Transport" subtitle="Routes, vehicles and student assignments">
      <div className="grid gap-4 sm:grid-cols-4">
        <StatCard title="Vehicles" value={summary?.total_vehicles ?? "—"} icon={Bus} />
        <StatCard title="Routes" value={summary?.total_routes ?? "—"} icon={MapPin} />
        <StatCard title="Students" value={summary?.students_using_transport ?? "—"} icon={Users} />
        <StatCard title="Utilization" value={summary ? `${summary.utilization_rate}%` : "—"} icon={Bus} />
      </div>

      <Tabs defaultValue="routes">
        <TabsList>
          <TabsTrigger value="routes">Routes</TabsTrigger>
          <TabsTrigger value="vehicles">Vehicles</TabsTrigger>
        </TabsList>
        <TabsContent value="routes" className="mt-4">
          <DataTable columns={routeCols} data={routes ?? []} loading={loadingRoutes} keyField="id" emptyMessage="No routes found." />
        </TabsContent>
        <TabsContent value="vehicles" className="mt-4">
          <DataTable columns={vehicleCols} data={vehicles ?? []} loading={loadingVehicles} keyField="id" emptyMessage="No vehicles found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
