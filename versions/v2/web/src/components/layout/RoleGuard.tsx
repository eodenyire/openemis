"use client";

import { useAuthStore } from "@/lib/auth";

interface RoleGuardProps {
  allowed: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * Renders children only if the current user's role is in `allowed`.
 * Shows `fallback` (default: access denied message) otherwise.
 */
export function RoleGuard({ allowed, children, fallback }: RoleGuardProps) {
  const user = useAuthStore((s) => s.user);
  const role = user?.role ?? "";

  if (!allowed.includes(role)) {
    return (
      <>
        {fallback ?? (
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            You don&apos;t have permission to view this page.
          </div>
        )}
      </>
    );
  }

  return <>{children}</>;
}
