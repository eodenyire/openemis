"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { ReportDownloadButton } from "@/components/shared/ReportDownloadButton";
import { Badge } from "@/components/ui/badge";

// API returns: id, tsc_number, job_title, employment_status, employment_type
const columns: Column<any>[] = [
  { key: "tsc_number", header: "TSC No", render: (r: any) => r.tsc_number ?? "—" },
  { key: "job_title", header: "Job Title", render: (r: any) => r.job_title ?? "—" },
  { key: "employment_type", header: "Type" },
  {
    key: "employment_status",
    header: "Status",
    render: (r: any) => (
      <Badge variant={r.employment_status === "active" ? "default" : "secondary"}>
        {r.employment_status}
      </Badge>
    ),
  },
];

export default function TeachersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["staff"],
    queryFn: () =>
      api.get<any[]>("/hr/staff/").then((r) => r.data),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Teachers / Staff</h2>
          <p className="text-muted-foreground text-sm">
            {data?.length ?? 0} staff members
          </p>
        </div>
        <div className="flex gap-2">
          <ReportDownloadButton
            label="Staff Directory"
            endpoint="/reports/staff/directory/excel"
            filename="staff-directory.xlsx"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data ?? []}
        loading={isLoading}
        keyField="id"
        emptyMessage="No staff found."
      />
    </div>
  );
}
