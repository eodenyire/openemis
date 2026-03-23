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

interface Announcement {
  id: number; title: string; body: string; audience: string;
  priority: string; is_published: boolean; views: number; created_at: string;
}

const priorityVariant = (p: string) =>
  p === "urgent" ? "destructive" : p === "high" ? "secondary" : "outline";

const cols: Column<Announcement>[] = [
  { key: "title", header: "Title" },
  { key: "audience", header: "Audience", render: (r) => <Badge variant="outline">{r.audience}</Badge> },
  { key: "priority", header: "Priority", render: (r) => <Badge variant={priorityVariant(r.priority)}>{r.priority}</Badge> },
  { key: "is_published", header: "Status", render: (r) => <Badge variant={r.is_published ? "default" : "secondary"}>{r.is_published ? "Published" : "Draft"}</Badge> },
  { key: "views", header: "Views" },
  { key: "created_at", header: "Date", render: (r) => r.created_at?.split("T")[0] ?? "—" },
];

export default function AnnouncementsPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: "", body: "", audience: "all", priority: "normal", is_published: true });

  const { data, isLoading } = useQuery({
    queryKey: ["announcements"],
    queryFn: () =>
      api.get<{ items: Announcement[]; total: number }>("/announcements/?published_only=false&limit=100").then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: (b: object) => api.post("/announcements/", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["announcements"] }); setOpen(false); },
  });

  return (
    <PageShell title="Announcements" subtitle="School-wide communications"
      actions={<Button size="sm" onClick={() => setOpen(true)}>+ New Announcement</Button>}
    >
      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id" emptyMessage="No announcements." />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Announcement</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Title</Label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
            <div><Label>Body</Label><Input value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Audience</Label>
                <select className="w-full border rounded px-3 py-2 text-sm" value={form.audience}
                  onChange={(e) => setForm({ ...form, audience: e.target.value })}>
                  <option value="all">All</option><option value="parents">Parents</option>
                  <option value="students">Students</option><option value="teachers">Teachers</option>
                </select>
              </div>
              <div><Label>Priority</Label>
                <select className="w-full border rounded px-3 py-2 text-sm" value={form.priority}
                  onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                  <option value="low">Low</option><option value="normal">Normal</option>
                  <option value="high">High</option><option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
            <Button className="w-full" disabled={create.isPending} onClick={() => create.mutate(form)}>
              {create.isPending ? "Publishing..." : "Publish"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
