"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { StatCard } from "@/components/shared/StatCard";
import { Users, UserCheck, DollarSign, CalendarCheck, BookOpen, AlertTriangle } from "lucide-react";
import { useAuthStore } from "@/lib/auth";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  // Role-aware summary from the backend
  const { data: summary, isLoading } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => api.get("/dashboard/summary").then((r) => r.data),
  });

  // Admin-level counts (only fetched when admin)
  const { data: students } = useQuery({
    queryKey: ["students-count"],
    enabled: ["admin", "super_admin", "school_admin", "registrar"].includes(user?.role ?? ""),
    queryFn: () => api.get("/students/").then((r) => r.data),
  });

  const { data: finance } = useQuery({
    queryKey: ["finance-summary"],
    enabled: ["admin", "super_admin", "school_admin", "finance_officer"].includes(user?.role ?? ""),
    queryFn: () => api.get("/finance/summary").then((r) => r.data),
  });

  const { data: analytics } = useQuery({
    queryKey: ["analytics-overview"],
    enabled: ["admin", "super_admin", "school_admin", "academic_director"].includes(user?.role ?? ""),
    queryFn: () => api.get("/analytics/overview").then((r) => r.data),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          {summary?.message ?? "Welcome to CBC EMIS Kenya"}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Students"
          value={students?.total ?? summary?.total_students ?? "—"}
          icon={Users}
          loading={isLoading}
        />
        <StatCard
          title="Total Teachers"
          value={summary?.total_teachers ?? "—"}
          icon={UserCheck}
          loading={isLoading}
        />
        <StatCard
          title="Fee Collection"
          value={
            finance?.collection_rate_pct != null
              ? `${finance.collection_rate_pct.toFixed(1)}%`
              : summary?.fee_collected_kes != null
              ? `KES ${Number(summary.fee_collected_kes).toLocaleString()}`
              : "—"
          }
          icon={DollarSign}
          loading={isLoading}
        />
        <StatCard
          title="Attendance Today"
          value={
            analytics?.attendance_rate != null
              ? `${analytics.attendance_rate.toFixed(1)}%`
              : summary?.attendance_today != null
              ? summary.attendance_today
              : "—"
          }
          icon={CalendarCheck}
          loading={isLoading}
        />
      </div>

      {/* Secondary stats row */}
      {(summary?.upcoming_exams != null || summary?.fees_due_kes != null) && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {summary?.upcoming_exams != null && (
            <StatCard
              title="Upcoming Exams"
              value={summary.upcoming_exams}
              icon={BookOpen}
              loading={isLoading}
            />
          )}
          {summary?.fees_due_kes != null && (
            <StatCard
              title="Fees Due"
              value={`KES ${Number(summary.fees_due_kes).toLocaleString()}`}
              icon={AlertTriangle}
              loading={isLoading}
            />
          )}
          {finance?.overdue_invoices != null && (
            <StatCard
              title="Overdue Invoices"
              value={finance.overdue_invoices}
              icon={AlertTriangle}
              loading={isLoading}
            />
          )}
        </div>
      )}
    </div>
  );
}
