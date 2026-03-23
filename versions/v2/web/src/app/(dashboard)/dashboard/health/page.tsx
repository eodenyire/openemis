"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DataTable, type Column } from "@/components/shared/DataTable";
import { PageShell } from "@/components/shared/PageShell";
import { StatCard } from "@/components/shared/StatCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Heart, Activity } from "lucide-react";

interface HealthRecord { id: number; student_id: number; height_cm: number; weight_kg: number; bmi: number; blood_group: string | null; created_at: string; }
interface ClinicVisit { id: number; student_id: number; visit_date: string; complaint: string; diagnosis: string | null; treatment: string | null; }
interface Vaccination { id: number; student_id: number; vaccine_name: string; date_given: string; next_due: string | null; }

const healthCols: Column<HealthRecord>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "height_cm", header: "Height (cm)" },
  { key: "weight_kg", header: "Weight (kg)" },
  { key: "bmi", header: "BMI", render: (r) => Number(r.bmi).toFixed(1) },
  { key: "blood_group", header: "Blood Group", render: (r) => r.blood_group ?? "—" },
  { key: "created_at", header: "Recorded", render: (r) => r.created_at?.split("T")[0] ?? "—" },
];

const clinicCols: Column<ClinicVisit>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "visit_date", header: "Date" },
  { key: "complaint", header: "Complaint" },
  { key: "diagnosis", header: "Diagnosis", render: (r) => r.diagnosis ?? "—" },
  { key: "treatment", header: "Treatment", render: (r) => r.treatment ?? "—" },
];

const vaccineCols: Column<Vaccination>[] = [
  { key: "student_id", header: "Student ID" },
  { key: "vaccine_name", header: "Vaccine" },
  { key: "date_given", header: "Date Given" },
  { key: "next_due", header: "Next Due", render: (r) => r.next_due ?? "—" },
];

export default function HealthPage() {
  const { data: records, isLoading: loadingRecords } = useQuery({
    queryKey: ["health-records"],
    queryFn: () => api.get<{ total: number; items: HealthRecord[] }>("/health/records/?limit=100").then((r) => r.data),
  });

  const { data: visits, isLoading: loadingVisits } = useQuery({
    queryKey: ["clinic-visits"],
    queryFn: () => api.get<{ total: number; items: ClinicVisit[] }>("/health/clinic/?limit=100").then((r) => r.data),
  });

  const { data: vaccinations, isLoading: loadingVaccinations } = useQuery({
    queryKey: ["vaccinations"],
    queryFn: () => api.get<{ total: number; items: Vaccination[] }>("/health/vaccinations/?limit=100").then((r) => r.data),
  });

  return (
    <PageShell title="Health" subtitle="Student health records, clinic visits and vaccinations"
      reports={[{ label: "Health Report", endpoint: "/reports/support/health/excel", filename: "health.xlsx" }]}
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Health Records" value={records?.total ?? "—"} icon={Heart} />
        <StatCard title="Clinic Visits" value={visits?.total ?? "—"} icon={Activity} />
        <StatCard title="Vaccinations" value={vaccinations?.total ?? "—"} icon={Heart} />
      </div>

      <Tabs defaultValue="records">
        <TabsList>
          <TabsTrigger value="records">Health Records</TabsTrigger>
          <TabsTrigger value="clinic">Clinic Visits</TabsTrigger>
          <TabsTrigger value="vaccinations">Vaccinations</TabsTrigger>
        </TabsList>
        <TabsContent value="records" className="mt-4">
          <DataTable columns={healthCols} data={records?.items ?? []} loading={loadingRecords} keyField="id" emptyMessage="No health records." />
        </TabsContent>
        <TabsContent value="clinic" className="mt-4">
          <DataTable columns={clinicCols} data={visits?.items ?? []} loading={loadingVisits} keyField="id" emptyMessage="No clinic visits." />
        </TabsContent>
        <TabsContent value="vaccinations" className="mt-4">
          <DataTable columns={vaccineCols} data={vaccinations?.items ?? []} loading={loadingVaccinations} keyField="id" emptyMessage="No vaccination records." />
        </TabsContent>
      </Tabs>
    </PageShell>
  );
}
