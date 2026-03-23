"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth";

interface AuthGuardProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export function AuthGuard({ children, allowedRoles }: AuthGuardProps) {
  const router = useRouter();
  const { token, user, initFromStorage } = useAuthStore();
  const [hydrated, setHydrated] = useState(false);

  // Step 1: hydrate from localStorage on mount
  useEffect(() => {
    initFromStorage();
    setHydrated(true);
  }, [initFromStorage]);

  // Step 2: once hydrated, check auth
  useEffect(() => {
    if (!hydrated) return;
    const stored = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
    if (!stored) {
      router.replace("/login");
      return;
    }
    if (allowedRoles && user && !allowedRoles.includes(user.role)) {
      router.replace("/unauthorized");
    }
  }, [hydrated, router, allowedRoles, user]);

  // While hydrating, render nothing (avoids flash redirect)
  if (!hydrated) return null;

  // Not authenticated
  const stored = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  if (!stored) return null;

  // Wrong role
  if (allowedRoles && user && !allowedRoles.includes(user.role)) return null;

  return <>{children}</>;
}
