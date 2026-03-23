"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ExamSession { id: number; name: string; start_date: string; end_date: string; state: string; }
interface Exam { id: number; name: string; exam_code: string; start_time: string; total_marks: number; state: string; subject?: { name: string }; }
interface Attendee { id: number; student_id: number; marks: number; state: string; exam?: { name: string }; }

const sessionCols: Column<ExamSession>[] = [
  { key: "name", header: "Session" },
  { key: "start_date", header: "Start" },
  { key: "end_date", header: "End" },
  { key: "state", header: "State", render: (r) => <Badge variant="secondary">{r.state}</Badge> },
];

const examCols: Column<Exam>[] = [
  { key: "exam_code", header: "Code" },
  { key: "name", header: "Exam" },
  { key: "subject", header: "Subject", render: (r) => r.subject?.name ?? "—" },
  { key: "start_time", header: "Date", render: (r) => r.start_time?.split("T")[0] ?? "—" },
  { key: "total_marks", header: "Total Marks" },
  { key: "state", header: "State", render: (r) => <Badge variant="secondary">{r.state}</Badge> },
];

const attendeeCols: Column<Attendee>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "marks", header: "Marks" },
  {
    key: "state",
    header: "Result",
    render: (r) => (
      <Badge variant={r.state === "pass" ? "default" : r.state === "fail" ? "destructive" : "secondary"}>
        {r.state}
      </Badge>
    ),
  },
];

export default function ExamsPage() {
  const [selectedSession, setSelectedSession] = useState<number | null>(null);
  const [selectedExam, setSelectedExam] = useState<number | null>(null);

  const { data: sessions, isLoading: loadingSessions } = useQuery({
    queryKey: ["exam-sessions"],
    queryFn: () => api.get<{ items: ExamSession[] }>("/exams/sessions/").then((r) => r.data),
  });

  const { data: exams, isLoading: loadingExams } = useQuery({
    queryKey: ["exams", selectedSession],
    queryFn: () =>
      api.get<{ items: Exam[] }>("/exams/", { params: { session_id: selectedSession, limit: 100 } }).then((r) => r.data),
    enabled: !!selectedSession,
  });

  const { data: attendees, isLoading: loadingAttendees } = useQuery({
    queryKey: ["exam-attendees", selectedExam],
    queryFn: () =>
      api.get<{ items: Attendee[] }>(`/exams/${selectedExam}/attendees/`).then((r) => r.data),
    enabled: !!selectedExam,
  });

  return (
    <PageShell
      title="Exams"
      subtitle="Exam sessions, papers and results"
      reports={
        selectedExam
          ? [{ label: "Result Slips PDF", endpoint: `/reports/exams/result-slips/pdf?exam_id=${selectedExam}`, filename: "result-slips.pdf" }]
          : []
      }
    >
      <div>
        <p className="text-sm font-medium mb-2">Exam Sessions</p>
        <DataTable
          columns={[
            ...sessionCols,
            {
              key: "id", header: "Action",
              render: (row) => (
                <Button size="sm" variant={selectedSession === row.id ? "default" : "outline"}
                  onClick={() => { setSelectedSession(row.id === selectedSession ? null : row.id); setSelectedExam(null); }}>
                  {selectedSession === row.id ? "Selected" : "View Exams"}
                </Button>
              ),
            },
          ]}
          data={sessions?.items ?? []}
          loading={loadingSessions}
          keyField="id"
          emptyMessage="No exam sessions found."
        />
      </div>

      {selectedSession && (
        <div>
          <p className="text-sm font-medium mb-2">Exams in Session</p>
          <DataTable
            columns={[
              ...examCols,
              {
                key: "id", header: "Results",
                render: (row) => (
                  <Button size="sm" variant={selectedExam === row.id ? "default" : "outline"}
                    onClick={() => setSelectedExam(row.id === selectedExam ? null : row.id)}>
                    {selectedExam === row.id ? "Hide" : "Results"}
                  </Button>
                ),
              },
            ]}
            data={exams?.items ?? []}
            loading={loadingExams}
            keyField="id"
            emptyMessage="No exams in this session."
          />
        </div>
      )}

      {selectedExam && (
        <div>
          <p className="text-sm font-medium mb-2">Attendees & Results</p>
          <DataTable
            columns={attendeeCols}
            data={attendees?.items ?? []}
            loading={loadingAttendees}
            keyField="id"
            emptyMessage="No results recorded yet."
          />
        </div>
      )}
    </PageShell>
  );
}
