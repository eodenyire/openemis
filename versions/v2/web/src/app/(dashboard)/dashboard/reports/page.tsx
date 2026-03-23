"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ReportDownloadButton } from "@/components/shared/ReportDownloadButton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ReportItem {
  label: string;
  endpoint: string;
  filename: string;
}

const studentReports: ReportItem[] = [
  { label: "Student List (Excel)", endpoint: "/reports/students/list/excel", filename: "students.xlsx" },
  { label: "Student List (PDF)", endpoint: "/reports/students/list/pdf", filename: "students.pdf" },
  { label: "Performance Report", endpoint: "/reports/students/performance/excel", filename: "performance.xlsx" },
  { label: "Attendance Report", endpoint: "/reports/students/attendance/excel", filename: "student-attendance.xlsx" },
  { label: "Health Records", endpoint: "/reports/students/health/excel", filename: "health-records.xlsx" },
];

const staffReports: ReportItem[] = [
  { label: "Teacher Directory", endpoint: "/reports/staff/directory/excel", filename: "staff-directory.xlsx" },
  { label: "TPAD Report", endpoint: "/reports/staff/tpad/excel", filename: "tpad.xlsx" },
  { label: "Leave Report", endpoint: "/reports/staff/leave/excel", filename: "leave-report.xlsx" },
  { label: "Payroll Report", endpoint: "/reports/staff/payroll/excel", filename: "payroll.xlsx" },
];

const financeReports: ReportItem[] = [
  { label: "Fee Collection", endpoint: "/reports/finance/fee-collection/excel", filename: "fee-collection.xlsx" },
  { label: "Outstanding Fees", endpoint: "/reports/finance/outstanding/excel", filename: "outstanding.xlsx" },
  { label: "Payment Methods", endpoint: "/reports/finance/payment-methods/excel", filename: "payment-methods.xlsx" },
];

const academicReports: ReportItem[] = [
  { label: "Exam Results", endpoint: "/reports/academic/exam-results/excel", filename: "exam-results.xlsx" },
  { label: "Report Cards (PDF)", endpoint: "/reports/academic/report-cards/pdf", filename: "report-cards.pdf" },
  { label: "LMS Activity", endpoint: "/reports/academic/lms/excel", filename: "lms-activity.xlsx" },
  { label: "Lesson Plans", endpoint: "/reports/academic/lesson-plans/excel", filename: "lesson-plans.xlsx" },
];

const supportReports: ReportItem[] = [
  { label: "Library Report", endpoint: "/reports/support/library/excel", filename: "library.xlsx" },
  { label: "Hostel Report", endpoint: "/reports/support/hostel/excel", filename: "hostel.xlsx" },
  { label: "Transport Report", endpoint: "/reports/support/transport/excel", filename: "transport.xlsx" },
  { label: "Health Report", endpoint: "/reports/support/health/excel", filename: "health.xlsx" },
];

const trendReports: ReportItem[] = [
  { label: "Enrollment Trends", endpoint: "/reports/trends/enrollment/excel", filename: "enrollment-trends.xlsx" },
  { label: "Performance Trends", endpoint: "/reports/trends/performance/excel", filename: "performance-trends.xlsx" },
  { label: "Fee Trends", endpoint: "/reports/trends/fees/excel", filename: "fee-trends.xlsx" },
  { label: "Attendance Trends", endpoint: "/reports/trends/attendance/excel", filename: "attendance-trends.xlsx" },
];

function ReportGroup({ reports }: { reports: ReportItem[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {reports.map((r) => (
        <ReportDownloadButton
          key={r.endpoint}
          label={r.label}
          endpoint={r.endpoint}
          filename={r.filename}
        />
      ))}
    </div>
  );
}

export default function ReportsPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Reports</h2>
        <p className="text-muted-foreground text-sm">Download school reports</p>
      </div>

      <Tabs defaultValue="students">
        <TabsList className="flex-wrap h-auto gap-1">
          <TabsTrigger value="students">Students</TabsTrigger>
          <TabsTrigger value="staff">Staff</TabsTrigger>
          <TabsTrigger value="finance">Finance</TabsTrigger>
          <TabsTrigger value="academic">Academic</TabsTrigger>
          <TabsTrigger value="support">Support</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="students">
          <Card>
            <CardHeader><CardTitle className="text-base">Student Reports</CardTitle></CardHeader>
            <CardContent><ReportGroup reports={studentReports} /></CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="staff">
          <Card>
            <CardHeader><CardTitle className="text-base">Staff Reports</CardTitle></CardHeader>
            <CardContent><ReportGroup reports={staffReports} /></CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="finance">
          <Card>
            <CardHeader><CardTitle className="text-base">Finance Reports</CardTitle></CardHeader>
            <CardContent><ReportGroup reports={financeReports} /></CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="academic">
          <Card>
            <CardHeader><CardTitle className="text-base">Academic Reports</CardTitle></CardHeader>
            <CardContent><ReportGroup reports={academicReports} /></CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="support">
          <Card>
            <CardHeader><CardTitle className="text-base">Support Services Reports</CardTitle></CardHeader>
            <CardContent><ReportGroup reports={supportReports} /></CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends">
          <Card>
            <CardHeader><CardTitle className="text-base">Trend Reports</CardTitle></CardHeader>
            <CardContent><ReportGroup reports={trendReports} /></CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
