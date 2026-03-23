"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { StatCard } from "@/components/shared/StatCard";
import { CalendarCheck, DollarSign, ClipboardList, Award } from "lucide-react";

const STUDENT_ROLES = ["student", "STUDENT"];

export default function StudentPortalPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["student-dashboard"],
    queryFn: () => api.get("/student/dashboard").then((r) => r.data),
  });

  const { data: results } = useQuery({
    queryKey: ["student-results"],
    queryFn: () => api.get("/student/results").then((r) => r.data),
  });

  return (
    <AuthGuard allowedRoles={STUDENT_ROLES}>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Student Portal</h2>
          <p className="text-muted-foreground">
            {data?.name ?? "Welcome"} — {data?.admission_number}
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Attendance Rate"
            value={data?.attendance?.rate != null ? `${data.attendance.rate}%` : "—"}
            icon={CalendarCheck} loading={isLoading}
          />
          <StatCard
            title="Fee Balance"
            value={data?.fees?.balance != null
              ? `KES ${Number(data.fees.balance).toLocaleString()}` : "—"}
            icon={DollarSign} loading={isLoading}
          />
          <StatCard
            title="Pending Assignments"
            value={data?.pending_assignments ?? "—"}
            icon={ClipboardList} loading={isLoading}
          />
          <StatCard
            title="Exam Results"
            value={results?.total ?? "—"}
            icon={Award} loading={isLoading}
          />
        </div>

        {results?.results?.length > 0 && (
          <div className="rounded-lg border p-4">
            <h3 className="font-semibold mb-3">Recent Results</h3>
            <div className="divide-y">
              {results.results.slice(0, 10).map((r: {
                exam_id: number; exam_name: string; subject: string;
                marks: number; grade: string;
              }) => (
                <div key={r.exam_id} className="py-2 flex justify-between text-sm">
                  <span>{r.exam_name} {r.subject ? `— ${r.subject}` : ""}</span>
                  <span className="font-medium">{r.marks} ({r.grade})</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AuthGuard>
  );
}
