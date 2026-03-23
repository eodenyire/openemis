"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen } from "lucide-react";

interface Book { id: number; name: string; isbn: string | null; author: string | null; available_copies: number; total_copies: number; }
interface Movement { id: number; media_name: string; student_name: string; issue_date: string; return_date: string | null; state: string; }

const bookCols: Column<Book>[] = [
  { key: "name", header: "Title" },
  { key: "isbn", header: "ISBN", render: (r) => r.isbn ?? "—" },
  { key: "author", header: "Author", render: (r) => r.author ?? "—" },
  { key: "available_copies", header: "Available" },
  { key: "total_copies", header: "Total" },
];

const movementCols: Column<Movement>[] = [
  { key: "media_name", header: "Book" },
  { key: "student_name", header: "Student" },
  { key: "issue_date", header: "Issued" },
  { key: "return_date", header: "Returned", render: (r) => r.return_date ?? "—" },
  { key: "state", header: "Status", render: (r) => <Badge variant={r.state === "returned" ? "default" : "secondary"}>{r.state}</Badge> },
];

export default function LibraryPage() {
  const { data: books, isLoading: loadingBooks } = useQuery({
    queryKey: ["library-books"],
    queryFn: () => api.get<{ total: number; items: Book[] }>("/library/media/?limit=100").then((r) => r.data),
  });

  const { data: movements, isLoading: loadingMovements } = useQuery({
    queryKey: ["library-movements"],
    queryFn: () => api.get<{ total: number; items: Movement[] }>("/library/movements/?limit=100").then((r) => r.data),
  });

  const issued = movements?.items.filter((m) => m.state === "issued").length ?? 0;

  return (
    <PageShell title="Library" subtitle="Books, media and borrowing records"
      reports={[{ label: "Library Report", endpoint: "/reports/support/library/excel", filename: "library.xlsx" }]}
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total Books" value={books?.total ?? "—"} icon={BookOpen} />
        <StatCard title="Currently Issued" value={issued} icon={BookOpen} />
        <StatCard title="Total Movements" value={movements?.total ?? "—"} icon={BookOpen} />
      </div>

      <Tabs defaultValue="books">
        <TabsList>
          <TabsTrigger value="books">Books / Media</TabsTrigger>
          <TabsTrigger value="movements">Borrowing Records</TabsTrigger>
        </TabsList>
        <TabsContent value="books" className="mt-4">
          <DataTable columns={bookCols} data={books?.items ?? []} loading={loadingBooks} keyField="id" emptyMessage="No books found." />
        </TabsContent>
        <TabsContent value="movements" className="mt-4">
          <DataTable columns={movementCols} data={movements?.items ?? []} loading={loadingMovements} keyField="id" emptyMessage="No borrowing records." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
