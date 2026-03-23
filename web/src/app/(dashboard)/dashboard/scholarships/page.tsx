"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Briefcase } from "lucide-react";

interface Scholarship {
  id: number; student_id: number; type: string | null;
  amount: number; start_date: string; end_date: string | null; state: string;
}

const cols: Column<Scholarship>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "type", header: "Type", render: (r) => r.type ?? "—" },
  { key: "amount", header: "Amount", render: (r) => `KES ${Number(r.amount).toLocaleString()}` },
  { key: "start_date", header: "Start" },
  { key: "end_date", header: "End", render: (r) => r.end_date ?? "Ongoing" },
  { key: "state", header: "State", render: (r) => <Badge variant={r.state === "active" ? "default" : "secondary"}>{r.state}</Badge> },
];

export default function ScholarshipsPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ student_id: "", scholarship_type_id: "1", amount: "", start_date: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["scholarships"],
    queryFn: () => api.get<{ total: number; items: Scholarship[] }>("/scholarships/").then((r) => r.data),
  });

  const { data: types } = useQuery({
    queryKey: ["scholarship-types"],
    queryFn: () => api.get<{ id: number; name: string }[]>("/scholarships/types").then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: (b: object) => api.post("/scholarships/", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["scholarships"] }); setOpen(false); },
  });

  const totalValue = data?.items.reduce((s, i) => s + Number(i.amount), 0) ?? 0;
  const active = data?.items.filter((i) => i.state === "active").length ?? 0;

  return (
    <PageShell title="Scholarships & Bursaries" subtitle="Student financial support"
      actions={<Button size="sm" onClick={() => setOpen(true)}>+ Award Scholarship</Button>}
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Scholarships" value={data?.total ?? "—"} icon={Briefcase} />
        <StatCard title="Active" value={active} icon={Briefcase} />
        <StatCard title="Total Value" value={`KES ${totalValue.toLocaleString()}`} icon={Briefcase} />
      </div>

      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id" emptyMessage="No scholarships found." />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Award Scholarship</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Student ID</Label><Input value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} /></div>
            <div><Label>Type</Label>
              <select className="w-full border rounded px-3 py-2 text-sm" value={form.scholarship_type_id}
                onChange={(e) => setForm({ ...form, scholarship_type_id: e.target.value })}>
                {types?.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <div><Label>Amount (KES)</Label><Input type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} /></div>
            <div><Label>Start Date</Label><Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></div>
            <Button className="w-full" disabled={create.isPending}
              onClick={() => create.mutate({ ...form, student_id: Number(form.student_id), scholarship_type_id: Number(form.scholarship_type_id), amount: Number(form.amount) })}>
              {create.isPending ? "Saving..." : "Award"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
