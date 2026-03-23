"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface Facility {
  id: number; name: string; facility_type: string | null;
  location: string | null; capacity: number | null; active: boolean;
}

const cols: Column<Facility>[] = [
  { key: "name", header: "Facility" },
  { key: "facility_type", header: "Type", render: (r) => r.facility_type ?? "—" },
  { key: "location", header: "Location", render: (r) => r.location ?? "—" },
  { key: "capacity", header: "Capacity", render: (r) => r.capacity ?? "—" },
  { key: "active", header: "Status", render: (r) => <Badge variant={r.active ? "default" : "secondary"}>{r.active ? "Active" : "Inactive"}</Badge> },
];

export default function FacilitiesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", facility_type: "", location: "", capacity: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["facilities"],
    queryFn: () => api.get<{ total: number; items: Facility[] }>("/facilities/").then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: (b: object) => api.post("/facilities/", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["facilities"] }); setOpen(false); },
  });

  return (
    <PageShell title="Facilities" subtitle="School facilities management"
      actions={<Button size="sm" onClick={() => setOpen(true)}>+ Add Facility</Button>}
    >
      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id" emptyMessage="No facilities found." />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Add Facility</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div><Label>Type</Label><Input placeholder="e.g. Lab, Library, Hall" value={form.facility_type} onChange={(e) => setForm({ ...form, facility_type: e.target.value })} /></div>
            <div><Label>Location</Label><Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></div>
            <div><Label>Capacity</Label><Input type="number" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} /></div>
            <Button className="w-full" disabled={create.isPending}
              onClick={() => create.mutate({ ...form, capacity: form.capacity ? Number(form.capacity) : undefined })}>
              {create.isPending ? "Saving..." : "Save"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
