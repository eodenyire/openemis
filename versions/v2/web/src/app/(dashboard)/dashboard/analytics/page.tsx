"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, Users, TrendingUp, BookOpen } from "lucide-react";

interface EnrollmentTrend { year: string; enrolled: number; }
interface LowAttender { student_id: number; name: string; admission_number: string; attendance_rate: number; days_present: number; days_total: number; }

const trendCols: Column<EnrollmentTrend>[] = [
  { key: "year", header: "Academic Year" },
  { key: "enrolled", header: "Enrolled" },
];

const attCols: Column<LowAttender>[] = [
  { key: "name", header: "Student" },
  { key: "admission_number", header: "Adm No" },
  { key: "attendance_rate", header: "Rate", render: (r) => `${r.attendance_rate}%` },
  { key: "days_present", header: "Present" },
  { key: "days_total", header: "Total Days" },
];

export default function AnalyticsPage() {
  const { data: summary } = useQuery({ queryKey: ["analytics-summary"], queryFn: () => api.get<any>("/analytics/summary").then(r => r.data) });
  const { data: trends, isLoading: loadingTrends } = useQuery({ queryKey: ["enrollment-trends"], queryFn: () => api.get<EnrollmentTrend[]>("/analytics/enrollment/trends").then(r => r.data) });
  const { data: lowAttenders, isLoading: loadingAtt } = useQuery({ queryKey: ["low-attenders"], queryFn: () => api.get<LowAttender[]>("/analytics/attendance/low-attenders").then(r => r.data) });
  const { data: feeData } = useQuery({ queryKey: ["fee-analytics"], queryFn: () => api.get<any>("/analytics/fees/collection").then(r => r.data) });

  return (
    <PageShell title="Analytics" subtitle="School-wide performance and trends">
      <div className="grid gap-4 sm:grid-cols-4">
        <StatCard title="Total Students" value={summary?.total_students ?? "—"} icon={Users} />
        <StatCard title="Total Teachers" value={summary?.total_teachers ?? "—"} icon={Users} />
        <StatCard title="Attendance Rate" value={summary ? `${summary.overall_attendance_rate}%` : "—"} icon={TrendingUp} />
        <StatCard title="Report Cards Issued" value={summary?.report_cards_issued ?? "—"} icon={BookOpen} />
      </div>

      {feeData && (
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard title="Total Invoiced" value={`KES ${(feeData.total_invoiced ?? 0).toLocaleString()}`} icon={BarChart3} />
          <StatCard title="Collected" value={`KES ${(feeData.total_collected ?? 0).toLocaleString()}`} icon={BarChart3} />
          <StatCard title="Collection Rate" value={`${feeData.collection_rate ?? 0}%`} icon={TrendingUp} />
        </div>
      )}

      <Tabs defaultValue="enrollment">
        <TabsList>
          <TabsTrigger value="enrollment">Enrollment Trends</TabsTrigger>
          <TabsTrigger value="attendance">Low Attenders</TabsTrigger>
        </TabsList>
        <TabsContent value="enrollment" className="mt-4">
          <DataTable columns={trendCols} data={trends ?? []} loading={loadingTrends} keyField="year" emptyMessage="No enrollment data." />
        </TabsContent>
        <TabsContent value="attendance" className="mt-4">
          <p className="text-sm text-muted-foreground mb-3">Students below 75% attendance threshold</p>
          <DataTable columns={attCols} data={lowAttenders ?? []} loading={loadingAtt} keyField="student_id" emptyMessage="No at-risk students found." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
