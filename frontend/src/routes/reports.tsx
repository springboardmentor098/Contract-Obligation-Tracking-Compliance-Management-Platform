import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  BarChart3,
  Download,
  FileBarChart2,
  FileCheck2,
  FileClock,
  FileSpreadsheet,
  FileText,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { reports, reportFiles } from "@/lib/api/resources";
import { apiErrorMessage } from "@/lib/api/errors";
import type { Report } from "@/lib/api/types";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Reports | ContractIQ" },
      {
        name: "description",
        content: "Generate and export operational compliance and contract intelligence reports.",
      },
    ],
  }),
  component: ReportsPage,
});

const reportTypes = [
  {
    type: "Executive Summary Report",
    label: "Executive Summary",
    description: "Complete platform audit: contracts, obligations, renewals, compliance score, and activities.",
    icon: FileBarChart2,
  },
  {
    type: "Compliance Report",
    label: "Compliance Report",
    description: "Risk evaluation, contract compliance status, and obligation adherence health.",
    icon: ShieldCheck,
  },
  {
    type: "Contract Report",
    label: "Contract Report",
    description: "Full contract portfolio breakdown, categories, departments, and lifecycle status.",
    icon: FileText,
  },
  {
    type: "Obligation Report",
    label: "Obligation Report",
    description: "Upcoming deadlines, priorities, assigned owners, and completion progress.",
    icon: FileCheck2,
  },
  {
    type: "Renewal Report",
    label: "Renewal Report",
    description: "Upcoming renewals, expiry timelines, and renegotiation tracking.",
    icon: FileClock,
  },
  {
    type: "Audit Report",
    label: "Audit & Activity Report",
    description: "Complete chronological log of operational system events and user actions.",
    icon: BarChart3,
  },
];

import { useAuth } from "@/lib/auth/auth-context";
import { canGenerateReport } from "@/lib/auth/rbac-permissions";

function ReportsPage() {
  const { user } = useAuth();
  const client = useQueryClient();
  const [busy, setBusy] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  const canGenerate = canGenerateReport(user?.role);

  const list = useQuery({
    queryKey: ["reports"],
    queryFn: reports.list,
  });

  const generate = async (type: string) => {
    if (!canGenerate || busy !== null) return;
    setBusy(type);
    try {
      const dateSuffix = new Date().toLocaleDateString("en-CA");
      await reports.create({
        report_name: `${type.replace(" Report", "")} - ${dateSuffix}`,
        report_type: type,
      });
      await client.invalidateQueries({ queryKey: ["reports"] });
      toast.success(`${type} generated successfully.`);
    } catch (caught: unknown) {
      toast.error(apiErrorMessage(caught, `Unable to generate ${type}.`));
    } finally {
      setBusy(null);
    }
  };

  const download = async (report: Report, format: "pdf" | "csv" = "pdf") => {
    const downloadKey = `${report.id}-${format}`;
    if (downloading !== null) return;
    setDownloading(downloadKey);
    try {
      const { blobUrl, filename } = await reportFiles.download(report.id, format);
      const anchor = document.createElement("a");
      anchor.href = blobUrl;
      anchor.download = filename || `${report.report_name.replace(/\s+/g, "_")}.${format}`;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(blobUrl);
      toast.success(`Downloaded ${report.report_name} (${format.toUpperCase()})`);
    } catch (caught: unknown) {
      toast.error(
        apiErrorMessage(
          caught,
          `Unable to download ${report.report_name} in ${format.toUpperCase()} format.`,
        ),
      );
    } finally {
      setDownloading(null);
    }
  };

  return (
    <main className="mx-auto w-full max-w-7xl space-y-8 px-5 py-8 lg:px-8">
      <header className="flex items-start gap-4">
        <span className="grid size-11 place-items-center rounded-lg bg-jade/10 text-jade shadow-sm">
          <FileBarChart2 className="size-6" aria-hidden="true" />
        </span>
        <div>
          <h1 className="font-display text-2xl font-semibold leading-tight">Reports & Analytics</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Generate and download dynamic operational compliance reports directly from live database records.
          </p>
        </div>
      </header>

      {/* Report Generation Cards */}
      {canGenerate ? (
        <section aria-labelledby="generate-heading" className="space-y-3">
          <h2 id="generate-heading" className="font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Available Report Templates
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {reportTypes.map((item) => {
              const isGenerating = busy === item.type;
              return (
                <div
                  key={item.type}
                  className="flex flex-col justify-between rounded-lg border border-border/70 bg-card p-5 shadow-hairline transition-all hover:border-jade/40"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <item.icon className="size-5 text-jade" aria-hidden="true" />
                      <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                        Live Data
                      </span>
                    </div>
                    <h3 className="mt-4 font-display text-sm font-semibold text-foreground">
                      {item.label}
                    </h3>
                    <p className="mt-1 min-h-[40px] text-xs leading-relaxed text-muted-foreground">
                      {item.description}
                    </p>
                  </div>

                  <Button
                    className="mt-5 w-full justify-center"
                    size="sm"
                    onClick={() => generate(item.type)}
                    disabled={busy !== null}
                    aria-busy={isGenerating}
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 size-4 animate-spin" aria-hidden="true" />
                        Generating…
                      </>
                    ) : (
                      <>
                        <BarChart3 className="mr-2 size-4" aria-hidden="true" />
                        Generate Report
                      </>
                    )}
                  </Button>
                </div>
              );
            })}
          </div>
        </section>
      ) : null}

      {/* Generated Reports List */}
      <section aria-labelledby="history-heading" className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 id="history-heading" className="font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Generated Reports
          </h2>
          {list.data?.length ? (
            <span className="text-xs text-muted-foreground">{list.data.length} available</span>
          ) : null}
        </div>

        {list.isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border border-border/70 bg-card p-4 shadow-hairline"
              >
                <div className="space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-32" />
                </div>
                <div className="flex gap-2">
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-8 w-20" />
                </div>
              </div>
            ))}
          </div>
        ) : list.isError ? (
          <div
            role="alert"
            className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
          >
            {apiErrorMessage(list.error, "Failed to load generated reports.")}
          </div>
        ) : list.data?.length ? (
          <div className="space-y-3">
            {list.data.map((report) => (
              <article
                key={report.id}
                className="flex flex-col gap-3 rounded-lg border border-border/70 bg-card p-4 shadow-hairline sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-foreground">{report.report_name}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {report.report_type} · Generated by user #{report.generated_by}
                  </p>
                </div>

                <div className="flex shrink-0 items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => download(report, "pdf")}
                    disabled={downloading !== null}
                    aria-label={`Download ${report.report_name} as PDF`}
                    aria-busy={downloading === `${report.id}-pdf`}
                  >
                    {downloading === `${report.id}-pdf` ? (
                      <Loader2 className="mr-1.5 size-3.5 animate-spin" aria-hidden="true" />
                    ) : (
                      <Download className="mr-1.5 size-3.5" aria-hidden="true" />
                    )}
                    PDF
                  </Button>

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => download(report, "csv")}
                    disabled={downloading !== null}
                    aria-label={`Download ${report.report_name} as CSV`}
                    aria-busy={downloading === `${report.id}-csv`}
                  >
                    {downloading === `${report.id}-csv` ? (
                      <Loader2 className="mr-1.5 size-3.5 animate-spin" aria-hidden="true" />
                    ) : (
                      <FileSpreadsheet className="mr-1.5 size-3.5 text-jade" aria-hidden="true" />
                    )}
                    CSV
                  </Button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
            <FileBarChart2 className="mx-auto size-8 text-muted-foreground/60" aria-hidden="true" />
            <p className="mt-2 font-medium">No reports generated yet</p>
            <p className="mt-1 text-xs">Choose a template above to generate your first dynamic compliance report.</p>
          </div>
        )}
      </section>
    </main>
  );
}
