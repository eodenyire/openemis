"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, Download } from "lucide-react";
import api from "@/lib/api";

interface ReportDownloadButtonProps {
  label: string;
  endpoint: string;
  filename: string;
  variant?: "default" | "outline" | "secondary" | "ghost";
  size?: "default" | "sm" | "lg";
}

export function ReportDownloadButton({
  label,
  endpoint,
  filename,
  variant = "outline",
  size = "sm",
}: ReportDownloadButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    setLoading(true);
    try {
      const response = await api.get(endpoint, { responseType: "blob" });
      const blob = new Blob([response.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button variant={variant} size={size} onClick={handleDownload} disabled={loading}>
      {loading ? (
        <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
      ) : (
        <Download className="mr-2 h-3.5 w-3.5" />
      )}
      {label}
    </Button>
  );
}
