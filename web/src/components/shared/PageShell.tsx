import { ReactNode } from "react";
import { ReportDownloadButton } from "./ReportDownloadButton";

interface ReportBtn {
  label: string;
  endpoint: string;
  filename: string;
}

interface PageShellProps {
  title: string;
  subtitle?: string;
  reports?: ReportBtn[];
  actions?: ReactNode;
  children: ReactNode;
}

export function PageShell({ title, subtitle, reports, actions, children }: PageShellProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">{title}</h2>
          {subtitle && <p className="text-muted-foreground text-sm mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex gap-2 flex-wrap items-center">
          {reports?.map((r) => (
            <ReportDownloadButton key={r.endpoint} label={r.label} endpoint={r.endpoint} filename={r.filename} />
          ))}
          {actions}
        </div>
      </div>
      {children}
    </div>
  );
}
