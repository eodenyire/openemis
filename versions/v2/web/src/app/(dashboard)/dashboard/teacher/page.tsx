"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { StatCard } from "@/components/shared/StatCard";
import { BookOpen, Users, ClipboardList, Calendar } from "lucide-react";

const TEACHER_ROLES = ["teacher", "TEACHER"];

export default function TeacherPortalPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["teacher-dashboard"],
    queryFn: () => api.get("/teacher/dashboard").then((r) => r.data),
  });

  const { data: classes } = useQuery({
    queryKey: ["teacher-classes"],
    queryFn: () => api.get("/teacher/classes").then((r) => r.data),
  });

  return (
    <AuthGuard allowedRoles={TEACHER_ROLES}>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Teacher Portal</h2>
          <p className="text-muted-foreground">
            {data?.name ?? "Welcome"} — {data?.employee_id}
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="My Classes" value={data?.classes_count ?? "—"}
            icon={Users} loading={isLoading} />
          <StatCard title="Subjects" value={data?.subjects?.length ?? "—"}
            icon={BookOpen} loading={isLoading} />
          <StatCard title="Pending Assignments" value={data?.pending_assignments ?? "—"}
            icon={ClipboardList} loading={isLoading} />
          <StatCard title="Upcoming Exams" value={data?.upcoming_exams ?? "—"}
            icon={Calendar} loading={isLoading} />
        </div>

        {classes && classes.length > 0 && (
          <div className="rounded-lg border p-4">
            <h3 className="font-semibold mb-3">My Classes</h3>
            <div className="divide-y">
              {classes.map((c: { course_id: number; course_name: string; student_count: number }) => (
                <div key={c.course_id} className="py-2 flex justify-between text-sm">
                  <span>{c.course_name}</span>
                  <span className="text-muted-foreground">{c.student_count} students</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AuthGuard>
  );
}
