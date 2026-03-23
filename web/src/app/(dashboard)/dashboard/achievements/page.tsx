"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Achievement { id: number; student_id: number; title: string; date: string; type: string | null; certificate_number: string | null; }
interface Activity { id: number; student_id: number; name: string; date: string; status: string; type: string | null; }

const achCols: Column<Achievement>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "title", header: "Achievement" },
  { key: "type", header: "Type", render: (r) => r.type ?? "—" },
  { key: "date", header: "Date" },
  { key: "certificate_number", header: "Certificate #", render: (r) => r.certificate_number ?? "—" },
];

const actCols: Column<Activity>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "name", header: "Activity" },
  { key: "type", header: "Type", render: (r) => r.type ?? "—" },
  { key: "date", header: "Date" },
  { key: "status", header: "Status" },
];

export default function AchievementsPage() {
  const qc = useQueryClient();
  const [openAch, setOpenAch] = useState(false);
  const [openAct, setOpenAct] = useState(false);
  const [achForm, setAchForm] = useState({ student_id: "", title: "", date: "" });
  const [actForm, setActForm] = useState({ student_id: "", name: "", date: "" });

  const { data: achievements, isLoading: loadingAch } = useQuery({
    queryKey: ["achievements"],
    queryFn: () => api.get<{ items: Achievement[] }>("/achievements/").then((r) => r.data),
  });

  const { data: activities, isLoading: loadingAct } = useQuery({
    queryKey: ["activities"],
    queryFn: () => api.get<{ items: Activity[] }>("/activities/").then((r) => r.data),
  });

  const createAch = useMutation({
    mutationFn: (b: object) => api.post("/achievements/", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["achievements"] }); setOpenAch(false); },
  });

  const createAct = useMutation({
    mutationFn: (b: object) => api.post("/activities/", b),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["activities"] }); setOpenAct(false); },
  });

  return (
    <PageShell title="Achievements & Activities" subtitle="Student co-curricular records">
      <Tabs defaultValue="achievements">
        <TabsList>
          <TabsTrigger value="achievements">Achievements</TabsTrigger>
          <TabsTrigger value="activities">Activities</TabsTrigger>
        </TabsList>

        <TabsContent value="achievements" className="space-y-4 mt-4">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => setOpenAch(true)}>+ Add Achievement</Button>
          </div>
          <DataTable columns={achCols} data={achievements?.items ?? []} loading={loadingAch} keyField="id" emptyMessage="No achievements recorded." />
        </TabsContent>

        <TabsContent value="activities" className="space-y-4 mt-4">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => setOpenAct(true)}>+ Add Activity</Button>
          </div>
          <DataTable columns={actCols} data={activities?.items ?? []} loading={loadingAct} keyField="id" emptyMessage="No activities recorded." />
        </TabsContent>
      </Tabs>

      <Dialog open={openAch} onOpenChange={setOpenAch}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Achievement</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Student ID</Label><Input value={achForm.student_id} onChange={(e) => setAchForm({ ...achForm, student_id: e.target.value })} /></div>
            <div><Label>Title</Label><Input value={achForm.title} onChange={(e) => setAchForm({ ...achForm, title: e.target.value })} /></div>
            <div><Label>Date</Label><Input type="date" value={achForm.date} onChange={(e) => setAchForm({ ...achForm, date: e.target.value })} /></div>
            <Button className="w-full" onClick={() => createAch.mutate({ ...achForm, student_id: Number(achForm.student_id) })} disabled={createAch.isPending}>
              {createAch.isPending ? "Saving..." : "Save"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={openAct} onOpenChange={setOpenAct}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Activity</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Student ID</Label><Input value={actForm.student_id} onChange={(e) => setActForm({ ...actForm, student_id: e.target.value })} /></div>
            <div><Label>Name</Label><Input value={actForm.name} onChange={(e) => setActForm({ ...actForm, name: e.target.value })} /></div>
            <div><Label>Date</Label><Input type="date" value={actForm.date} onChange={(e) => setActForm({ ...actForm, date: e.target.value })} /></div>
            <Button className="w-full" onClick={() => createAct.mutate({ ...actForm, student_id: Number(actForm.student_id) })} disabled={createAct.isPending}>
              {createAct.isPending ? "Saving..." : "Save"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageShell>
  );
}
