"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { StatCard } from "@/components/shared/StatCard";
import { Users, Bell, MessageSquare, DollarSign } from "lucide-react";

const PARENT_ROLES = ["parent", "PARENT"];

export default function ParentPortalPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["parent-dashboard"],
    queryFn: () => api.get("/parent/dashboard").then((r) => r.data),
  });

  return (
    <AuthGuard allowedRoles={PARENT_ROLES}>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Parent Portal</h2>
          <p className="text-muted-foreground">{data?.parent_name ?? "Welcome"}</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Children" value={data?.children?.length ?? "—"}
            icon={Users} loading={isLoading} />
          <StatCard title="Unread Notifications" value={data?.unread_notifications ?? "—"}
            icon={Bell} loading={isLoading} />
          <StatCard title="Open Messages" value={data?.open_messages ?? "—"}
            icon={MessageSquare} loading={isLoading} />
          <StatCard
            title="Total Fee Balance"
            value={data?.children
              ? `KES ${data.children.reduce((s: number, c: { fees: { balance: number } }) =>
                  s + (c.fees?.balance ?? 0), 0).toLocaleString()}`
              : "—"}
            icon={DollarSign} loading={isLoading}
          />
        </div>

        {data?.children?.map((child: {
          student_id: number; name: string; admission_number: string;
          class: string; fees: { total: number; paid: number; balance: number };
          attendance: { present: number; absent: number; rate: number };
        }) => (
          <div key={child.student_id} className="rounded-lg border p-4 space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold">{child.name}</p>
                <p className="text-sm text-muted-foreground">
                  {child.admission_number} · {child.class}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Attendance</p>
                <p className="font-medium">{child.attendance.rate}%
                  <span className="text-muted-foreground font-normal">
                    {" "}({child.attendance.present}P / {child.attendance.absent}A)
                  </span>
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Fee Balance</p>
                <p className="font-medium">
                  KES {Number(child.fees.balance).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </AuthGuard>
  );
}
