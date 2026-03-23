"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { ReportDownloadButton } from "@/components/shared/ReportDownloadButton";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import type { Student, PaginatedResponse } from "@/types";

const PAGE_SIZE = 20;

// API returns: admission_number, first_name, last_name, active, nemis_upi
const columns: Column<Student>[] = [
  { key: "admission_number" as keyof Student, header: "Adm No" },
  { key: "first_name" as keyof Student, header: "First Name" },
  { key: "last_name" as keyof Student, header: "Last Name" },
  { key: "gender", header: "Gender" },
  { key: "nemis_upi", header: "NEMIS UPI" },
  {
    key: "status",
    header: "Status",
    render: (row: any) => (
      <Badge variant={row.active ? "default" : "secondary"}>
        {row.active ? "active" : "inactive"}
      </Badge>
    ),
  },
];

export default function StudentsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["students", page, search],
    queryFn: () =>
      api
        .get<PaginatedResponse<Student>>("/students/", {
          params: { page, size: PAGE_SIZE, search: search || undefined },
        })
        .then((r) => r.data),
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Students</h2>
          <p className="text-muted-foreground text-sm">
            {data?.total ?? 0} students enrolled
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <ReportDownloadButton
            label="Excel"
            endpoint="/reports/students/list/excel"
            filename="students.xlsx"
          />
          <ReportDownloadButton
            label="PDF"
            endpoint="/reports/students/list/pdf"
            filename="students.pdf"
          />
        </div>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search students..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="pl-9"
        />
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        loading={isLoading}
        keyField="id"
        emptyMessage="No students found."
      />

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
