"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare } from "lucide-react";
import { StatCard } from "@/components/shared/StatCard";

interface SmsLog { id: number; recipient: string; message: string; status: string; sent_at: string; }

const cols: Column<SmsLog>[] = [
  { key: "recipient", header: "Recipient" },
  { key: "message", header: "Message", render: (r) => r.message.length > 60 ? r.message.slice(0, 60) + "…" : r.message },
  { key: "status", header: "Status", render: (r) => <Badge variant={r.status === "sent" ? "default" : r.status === "failed" ? "destructive" : "secondary"}>{r.status}</Badge> },
  { key: "sent_at", header: "Sent At", render: (r) => new Date(r.sent_at).toLocaleString() },
];

export default function SmsPage() {
  const qc = useQueryClient();
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["sms-logs"],
    queryFn: () => api.get<{ total: number; items: SmsLog[] }>("/sms/logs").then(r => r.data),
  });

  const send = useMutation({
    mutationFn: () => api.post("/sms/send", { phone, message }),
    onSuccess: () => { setPhone(""); setMessage(""); qc.invalidateQueries({ queryKey: ["sms-logs"] }); },
  });

  return (
    <PageShell title="SMS" subtitle="Send messages and view SMS logs">
      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard title="Total Sent" value={data?.total ?? "—"} icon={MessageSquare} />
        <StatCard title="Failed" value={data?.items.filter(s => s.status === "failed").length ?? "—"} icon={MessageSquare} />
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Send SMS</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <Label>Phone Number</Label>
            <Input placeholder="+254700000000" value={phone} onChange={e => setPhone(e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label>Message</Label>
            <Textarea placeholder="Type your message..." value={message} onChange={e => setMessage(e.target.value)} rows={3} />
          </div>
          <Button onClick={() => send.mutate()} disabled={!phone || !message || send.isPending}>
            {send.isPending ? "Sending…" : "Send SMS"}
          </Button>
        </CardContent>
      </Card>

      <DataTable columns={cols} data={data?.items ?? []} loading={isLoading} keyField="id" emptyMessage="No SMS logs found." />
    </PageShell>
  );
}
