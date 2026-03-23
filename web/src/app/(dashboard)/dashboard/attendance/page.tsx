"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { CalendarCheck, UserCheck, UserX } from "lucide-react";

interface Sheet {
  id: number;
  attendance_date: string;
  state: string;
  register_id: number;
  lines_count?: number;
}

interface Line {
  id: number;
  student_id: number;
  status: string;
  note: string;
  student?: { first_name: string; last_name: string; admission_number: string };
}

const sheetCols: Column<Sheet>[] = [
  { key: "id", header: "Sheet #" },
  { key: "attendance_date", header: "Date" },
  { key: "register_id", header: "Register" },
  {
    key: "state",
    header: "State",
    render: (r) => (
      <Badge variant={r.state === "done" ? "default" : "secondary"}>{r.state}</Badge>
    ),
  },
];

const lineCols: Column<Line>[] = [
  {
    key: "student",
    header: "Student",
    render: (r) => r.student ? `${r.student.first_name} ${r.student.last_name}` : `#${r.student_id}`,
  },
  { key: "student", header: "Adm No", render: (r) => r.student?.admission_number ?? "—" },
  {
    key: "status",
    header: "Status",
    render: (r) => (
      <Badge variant={r.status === "present" ? "default" : r.status === "late" ? "secondary" : "destructive"}>
        {r.status}
      </Badge>
    ),
  },
  { key: "note", header: "Note" },
];

export default function AttendancePage() {
  const today = new Date().toISOString().split("T")[0];
  const [dateFilter, setDateFilter] = useState(today);
  const [selectedSheet, setSelectedSheet] = useState<number | null>(null);

  const { data: sheets, isLoading } = useQuery({
    queryKey: ["attendance-sheets", dateFilter],
    queryFn: () =>
      api.get<Sheet[]>("/attendance/sheets/", { params: { limit: 100 } }).then((r) => r.data),
  });

  const filtered = sheets?.filter((s) => !dateFilter || s.attendance_date?.startsWith(dateFilter)) ?? [];

  const { data: lines, isLoading: loadingLines } = useQuery({
    queryKey: ["attendance-lines", selectedSheet],
    queryFn: () =>
      api.get<Line[]>(`/attendance/sheets/${selectedSheet}/lines`).then((r) => r.data),
    enabled: !!selectedSheet,
  });

  const present = lines?.filter((l) => l.status === "present").length ?? 0;
  const absent = lines?.filter((l) => l.status === "absent").length ?? 0;
  const total = lines?.length ?? 0;

  return (
    <PageShell
      title="Attendance"
      subtitle="Daily attendance registers"
      reports={[
        { label: "Attendance Report", endpoint: "/reports/students/attendance/excel", filename: "attendance.xlsx" },
      ]}
    >
      <div className="flex items-center gap-3">
        <Label htmlFor="date-filter">Filter by date</Label>
        <Input
          id="date-filter"
          type="date"
          value={dateFilter}
          onChange={(e) => { setDateFilter(e.target.value); setSelectedSheet(null); }}
          className="w-44"
        />
      </div>

      <DataTable
        columns={[
          ...sheetCols,
          {
            key: "id",
            header: "Action",
            render: (row) => (
              <button
                onClick={() => setSelectedSheet(row.id === selectedSheet ? null : row.id)}
                className={`text-xs px-3 py-1 rounded border transition-colors ${
                  selectedSheet === row.id
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-border hover:bg-accent"
                }`}
              >
                {selectedSheet === row.id ? "Hide" : "View Lines"}
              </button>
            ),
          },
        ]}
        data={filtered}
        loading={isLoading}
        keyField="id"
        emptyMessage="No attendance sheets for this date."
      />

      {selectedSheet && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard title="Present" value={present} icon={UserCheck} />
            <StatCard title="Absent" value={absent} icon={UserX} />
            <StatCard
              title="Rate"
              value={total > 0 ? `${((present / total) * 100).toFixed(1)}%` : "—"}
              icon={CalendarCheck}
            />
          </div>
          <DataTable
            columns={lineCols}
            data={lines ?? []}
            loading={loadingLines}
            keyField="id"
            emptyMessage="No lines in this sheet."
          />
        </div>
      )}
    </PageShell>
  );
}
