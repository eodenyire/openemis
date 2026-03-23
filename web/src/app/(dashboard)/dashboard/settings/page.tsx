"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useAuthStore } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";

export default function SettingsPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-4 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground text-sm">Account and system settings</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Account Information</CardTitle>
          <CardDescription>Your current session details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-sm text-muted-foreground">Username</span>
            <span className="text-sm font-medium">{user?.username ?? "—"}</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-muted-foreground">Role</span>
            <Badge variant="secondary" className="capitalize">
              {user?.role ?? "—"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">System</CardTitle>
          <CardDescription>Application configuration</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-sm text-muted-foreground">API URL</span>
            <span className="text-sm font-mono text-xs">
              {process.env.NEXT_PUBLIC_API_URL}
            </span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-muted-foreground">Version</span>
            <span className="text-sm">0.1.0</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
