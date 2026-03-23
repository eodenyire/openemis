"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth";

export default function UnauthorizedPage() {
  const router = useRouter();
  const { logout } = useAuthStore();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">Access Denied</h1>
      <p className="text-muted-foreground">You don&apos;t have permission to view this page.</p>
      <div className="flex gap-3">
        <button
          onClick={() => router.back()}
          className="px-4 py-2 rounded border text-sm"
        >
          Go Back
        </button>
        <button
          onClick={() => { logout(); router.replace("/login"); }}
          className="px-4 py-2 rounded bg-primary text-primary-foreground text-sm"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}
