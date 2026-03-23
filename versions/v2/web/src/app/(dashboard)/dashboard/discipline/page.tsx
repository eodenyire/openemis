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

interface DisciplineRecord {
  id: number; student_id: number; date: string;
  description: string; severity: string; action: string | null;
  reported_by: number; created_at: string;
}

const severityVariant = (s: string) =>
  s === "severe" ? "destructive" : s === "moderate" ? "secondary" : "outline";

const cols: Column<DisciplineRecord>[] = [
  { key: "id", header: "#" },
  { key: "student_id", header: "Student ID" },
  { key: "date", header: "Date" },
  { key: "description", header: "Description" },
  { key: "severity", header: "Severity", render: (r) => <Badge variant={severityVariant(r.severity)}>{r.severity}</Badge> },
  { key: "action", header: "Action Taken", render: (r) => r.action ?? "—" },
];

export default function DisciplinePage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ student_id: "", date: "", description: "", severity: "minor" });

  const { data, isLoading } = useQuery({
    queryKey: ["discipline"],
    queryFn: () => api.get<{ total: number; items: DisciplineRecord[] }>("/discipline/").then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: (body: object) => api.post("/discipline/", body),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["discipline"] }); setOpen(false); },
  });

  return (
    <PageShell title="Discipline" subtitle="Student discipline records"
      reports={[{ label: "Export", endpoint: "/reports/students/list/excel", filename: "discipline.xlsx" }]}
      actions={<Button size="sm" onClick={() => setOpen(true)}>+ New Record</Button>}
    >
      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id"
        emptyMessage="No discipline records." />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Discipline Record</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Student ID</Label>
              <Input value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} /></div>
            <div><Label>Date</Label>
              <Input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} /></div>
            <div><Label>Description</Label>
              <Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
            <div><Label>Severity</Label>
              <select className="w-full border rounded px-3 py-2 text-sm"
                value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
                <option value="minor">Minor</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </div>
            <Button className="w-full" onClick={() => create.mutate({ ...form, student_id: Number(form.student_id) })}
              disabled={create.isPending}>
              {create.isPending ? "Saving..." : "Save Record"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
