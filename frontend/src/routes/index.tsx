import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CalendarDays,
  CircleCheck,
  FilePlus2,
  ShieldAlert,
  UsersRound,
} from "lucide-react";
import { dashboardApi } from "@/lib/api/dashboard";
import {
  activities,
  compliance,
  contracts,
  notifications,
  obligations,
  renewals as renewalApi,
  users,
} from "@/lib/api/resources";
import { apiErrorMessage } from "@/lib/api/errors";
import { Skeleton } from "@/components/ui/skeleton";

export const Route = createFileRoute("/")({ component: Index });

function Index() {
  const summary = useQuery({ queryKey: ["dashboard", "summary"], queryFn: dashboardApi.summary });
  const renewals = useQuery({
    queryKey: ["dashboard", "upcoming-renewals"],
    queryFn: dashboardApi.upcomingRenewals,
  });
  const contractStatus = useQuery({
    queryKey: ["dashboard", "contract-status"],
    queryFn: dashboardApi.contractStatus,
  });
  const obligationStatus = useQuery({
    queryKey: ["dashboard", "obligation-status"],
    queryFn: dashboardApi.obligationStatus,
  });
  const obligationList = useQuery({ queryKey: ["obligations"], queryFn: obligations.list });
  const renewalList = useQuery({ queryKey: ["renewals"], queryFn: renewalApi.list });
  const contractList = useQuery({ queryKey: ["contracts"], queryFn: contracts.list });
  const userList = useQuery({ queryKey: ["users"], queryFn: users.list });
  const activityList = useQuery({ queryKey: ["activities"], queryFn: activities.list });
  const complianceList = useQuery({
    queryKey: ["compliance", "high-risk"],
    queryFn: compliance.highRisk,
  });
  const notificationList = useQuery({
    queryKey: ["notifications"],
    queryFn: notifications.list,
  });

  const failed = [
    summary,
    renewals,
    contractStatus,
    obligationStatus,
    obligationList,
    complianceList,
    notificationList,
    renewalList,
    contractList,
    userList,
    activityList,
  ].find((query) => query.isError);

  const isStatsLoading =
    userList.isLoading ||
    contractList.isLoading ||
    renewalList.isLoading ||
    complianceList.isLoading ||
    activityList.isLoading ||
    notificationList.isLoading;

  const overdue = (obligationList.data ?? []).filter((item) => item.status === "Overdue");
  const unread = (notificationList.data ?? []).filter((item) => item.status !== "Read");

  return (
    <main className="mx-auto w-full max-w-[1500px] px-5 py-7 lg:px-8">
      <header className="mb-7">
        <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-muted-foreground">
          Operational workspace
        </p>
        <h1 className="font-display text-3xl font-semibold leading-tight">Approval Queue</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">
          {summary.isLoading ? (
            "Loading workspace summary…"
          ) : (
            <>
              {summary.data?.contracts.total ?? 0} contracts ·{" "}
              {summary.data?.obligations.overdue ?? 0} overdue obligations
            </>
          )}
        </p>
      </header>

      {failed ? (
        <div
          role="alert"
          aria-live="assertive"
          className="mb-6 rounded-md border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
        >
          {apiErrorMessage(failed.error, "Unable to load dashboard data. Please check connection.")}
        </div>
      ) : null}

      <QuickActions />

      <AdminStats
        users={userList.data?.length ?? 0}
        contracts={contractList.data?.length ?? 0}
        renewals={renewalList.data?.length ?? 0}
        compliance={complianceList.data?.length ?? 0}
        activities={activityList.data?.length ?? 0}
        notifications={notificationList.data?.length ?? 0}
        isLoading={isStatsLoading}
      />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="space-y-6 xl:col-span-8">
          <RecentContracts items={contractList.data ?? []} isLoading={contractList.isLoading} />

          <Panel
            title="Upcoming renewals"
            count={summary.isLoading ? "Loading…" : `${summary.data?.renewals.upcoming ?? 0} upcoming`}
            icon={<CircleCheck className="size-4 text-jade" aria-hidden="true" />}
          >
            {renewals.isLoading ? (
              <PanelSkeleton count={3} />
            ) : (
              (renewals.data ?? []).map((item) => (
                <Row
                  key={item.id}
                  title={item.contract_title}
                  detail={item.status}
                  value={item.renewal_date}
                />
              ))
            )}
            <Empty
              show={!renewals.isLoading && !renewals.data?.length}
              text="No upcoming contract renewals scheduled within the next 30 days."
            />
          </Panel>

          <CalendarPanel
            obligations={obligationList.data ?? []}
            renewals={renewalList.data ?? []}
            isLoading={obligationList.isLoading || renewalList.isLoading}
          />

          <Panel
            title="Recent notifications"
            count={notificationList.isLoading ? "Loading…" : `${unread.length} unread`}
          >
            {notificationList.isLoading ? (
              <PanelSkeleton count={3} />
            ) : (
              unread.slice(0, 5).map((item) => (
                <Row
                  key={item.id}
                  title={item.title}
                  detail={item.message}
                  value={new Date(item.created_at).toLocaleDateString()}
                />
              ))
            )}
            <Empty
              show={!notificationList.isLoading && !unread.length}
              text="You're all caught up! No unread notifications."
            />
          </Panel>
        </div>

        <aside className="space-y-6 xl:col-span-4">
          <Panel
            title="Overdue obligations"
            count={obligationList.isLoading ? "Loading…" : `${overdue.length}`}
            icon={<AlertTriangle className="size-4 text-jade" aria-hidden="true" />}
          >
            {obligationList.isLoading ? (
              <PanelSkeleton count={2} />
            ) : (
              overdue.map((item) => (
                <Row
                  key={item.id}
                  title={item.title}
                  detail={item.obligation_type}
                  value={item.due_date}
                  emphasis
                />
              ))
            )}
            <Empty
              show={!obligationList.isLoading && !overdue.length}
              text="No overdue obligations. All contract tasks are on track."
            />
          </Panel>

          <Panel
            title="High-risk compliance"
            count={complianceList.isLoading ? "Loading…" : `${(complianceList.data ?? []).length}`}
            icon={<ShieldAlert className="size-4 text-jade" aria-hidden="true" />}
          >
            {complianceList.isLoading ? (
              <PanelSkeleton count={2} />
            ) : (
              (complianceList.data ?? []).map((item) => (
                <Row
                  key={item.contract_id}
                  title={item.contract_title}
                  detail={item.status}
                  value={item.risk_level}
                  emphasis
                />
              ))
            )}
            <Empty
              show={!complianceList.isLoading && !complianceList.data?.length}
              text="No high-risk contracts. Compliance risk level is nominal."
            />
          </Panel>

          <Panel title="Portfolio summary">
            <div className="grid grid-cols-2 gap-px bg-border text-xs">
              <Metric
                label="Active contracts"
                value={summary.data?.contracts.active ?? 0}
                isLoading={summary.isLoading}
              />
              <Metric
                label="Pending obligations"
                value={summary.data?.obligations.pending ?? 0}
                isLoading={summary.isLoading}
              />
              <Metric
                label="Renewals"
                value={summary.data?.renewals.total ?? 0}
                isLoading={summary.isLoading}
              />
              <Metric
                label="Expired contracts"
                value={summary.data?.contracts.expired ?? 0}
                isLoading={summary.isLoading}
              />
            </div>
          </Panel>

          <Panel title="Status analytics">
            <StatusGroup
              label="Contracts"
              items={contractStatus.data ?? []}
              isLoading={contractStatus.isLoading}
            />
            <StatusGroup
              label="Obligations"
              items={obligationStatus.data ?? []}
              isLoading={obligationStatus.isLoading}
            />
          </Panel>

          <Panel
            title="Recent activity"
            count={activityList.isLoading ? "Loading…" : `${activityList.data?.length ?? 0} events`}
          >
            <div className="divide-y divide-border/60">
              {activityList.isLoading ? (
                <PanelSkeleton count={3} />
              ) : (
                (activityList.data ?? [])
                  .slice(-5)
                  .reverse()
                  .map((item) => (
                    <Row
                      key={item.id}
                      title={item.activity}
                      detail={`Contract ${item.contract_id} · User ${item.user_id}`}
                      value={
                        item.created_at
                          ? new Date(item.created_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "—"
                      }
                    />
                  ))
              )}
              <Empty
                show={!activityList.isLoading && !activityList.data?.length}
                text="No recent system activities recorded."
              />
            </div>
          </Panel>
        </aside>
      </div>
    </main>
  );
}

function PanelSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3 p-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center gap-4">
          <Skeleton className="size-2 shrink-0 rounded-full" />
          <div className="min-w-0 flex-1 space-y-1.5">
            <Skeleton className="h-3.5 w-3/5" />
            <Skeleton className="h-2.5 w-2/5" />
          </div>
          <Skeleton className="h-3 w-14 shrink-0" />
        </div>
      ))}
    </div>
  );
}

function QuickActions() {
  const actions = [
    { label: "Contract", to: "/contracts" as const, icon: FilePlus2 },
    { label: "User", to: "/users" as const, icon: UsersRound },
    { label: "Obligation", to: "/obligations" as const, icon: FilePlus2 },
    { label: "Renewal", to: "/renewals" as const, icon: CalendarDays },
    { label: "Report", to: "/reports" as const, icon: FilePlus2 },
  ];
  return (
    <section className="mb-6 rounded-lg bg-card p-4 shadow-hairline" aria-label="Quick actions bar">
      <div className="flex flex-wrap items-center gap-2">
        <span className="mr-2 text-sm font-semibold">Quick actions</span>
        {actions.map((action) => (
          <Link
            key={action.label}
            to={action.to}
            aria-label={`Go to ${action.label} management`}
            className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm transition-colors hover:border-jade hover:text-jade"
          >
            <action.icon className="size-4" aria-hidden="true" />+ {action.label}
          </Link>
        ))}
      </div>
    </section>
  );
}

function AdminStats({
  users,
  contracts,
  renewals,
  compliance,
  activities,
  notifications,
  isLoading = false,
}: {
  users: number;
  contracts: number;
  renewals: number;
  compliance: number;
  activities: number;
  notifications: number;
  isLoading?: boolean;
}) {
  const stats = [
    { label: "Users", value: users },
    { label: "Contracts", value: contracts },
    { label: "Renewals", value: renewals },
    { label: "Compliance", value: compliance },
    { label: "Activities", value: activities },
    { label: "Notifications", value: notifications },
  ];
  return (
    <section
      aria-label="System overview statistics"
      className="mb-6 grid grid-cols-2 gap-px overflow-hidden rounded-lg bg-border shadow-hairline sm:grid-cols-3 lg:grid-cols-6"
    >
      {stats.map(({ label, value }) => (
        <div key={label} className="bg-card p-4">
          <p className="text-xs text-muted-foreground">{label}</p>
          {isLoading ? (
            <Skeleton className="mt-1 h-7 w-12" />
          ) : (
            <p className="mt-1 font-display text-2xl font-semibold text-jade">{value}</p>
          )}
        </div>
      ))}
    </section>
  );
}

function RecentContracts({
  items,
  isLoading = false,
}: {
  items: Array<{ id: number; title: string; status: string; updated_at: string }>;
  isLoading?: boolean;
}) {
  const recent = [...items].sort((a, b) => b.updated_at.localeCompare(a.updated_at)).slice(0, 5);
  return (
    <Panel title="Recent contracts" count="Latest edited">
      <div className="divide-y divide-border/60">
        {isLoading ? (
          <PanelSkeleton count={3} />
        ) : (
          recent.map((item) => (
            <Link
              key={item.id}
              to="/contracts/$contractId"
              params={{ contractId: String(item.id) }}
              aria-label={`View contract ${item.title}`}
            >
              <Row
                title={item.title}
                detail={item.status}
                value={item.updated_at ? new Date(item.updated_at).toLocaleDateString() : "—"}
              />
            </Link>
          ))
        )}
        <Empty show={!isLoading && !recent.length} text="No recent contracts found." />
      </div>
    </Panel>
  );
}

function CalendarPanel({
  obligations,
  renewals,
  isLoading = false,
}: {
  obligations: Array<{ id: number; title: string; due_date: string; status: string }>;
  renewals: Array<{ id: number; renewal_date: string; status: string }>;
  isLoading?: boolean;
}) {
  const today = new Date();
  const events = [
    ...obligations.map((item) => ({
      id: `o-${item.id}`,
      date: item.due_date,
      label: item.title,
      type: item.status === "Completed" ? "completed" : "deadline",
    })),
    ...renewals.map((item) => ({
      id: `r-${item.id}`,
      date: item.renewal_date,
      label: "Renewal",
      type: item.status === "Expired" ? "expired" : "renewal",
    })),
  ].sort((a, b) => a.date.localeCompare(b.date));

  return (
    <Panel
      title="Calendar"
      count={isLoading ? "Loading…" : `${events.length} tracked dates`}
      icon={<CalendarDays className="size-4 text-jade" aria-hidden="true" />}
    >
      {isLoading ? (
        <div className="grid gap-2 p-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="space-y-2 rounded-md border border-border/70 p-3">
              <Skeleton className="h-3 w-16" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-12" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid gap-2 p-5 sm:grid-cols-2 lg:grid-cols-3">
          {events.slice(0, 12).map((event) => {
            const days = Math.ceil(
              (new Date(`${event.date}T00:00:00`).getTime() -
                new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()) /
                86400000,
            );
            const tone =
              event.type === "expired" || days < 0
                ? "text-destructive"
                : days <= 30
                  ? "text-amber-700"
                  : "text-jade";
            return (
              <div key={event.id} className="rounded-md border border-border/70 p-3">
                <p className="text-xs text-muted-foreground">{event.date}</p>
                <p className="mt-1 truncate text-sm font-medium">{event.label}</p>
                <p className={`mt-1 text-xs ${tone}`}>
                  {event.type === "expired" || days < 0
                    ? "Expired"
                    : days === 0
                      ? "Today"
                      : `${days} days`}
                </p>
              </div>
            );
          })}
          {!events.length ? (
            <p className="col-span-full py-4 text-center text-sm text-muted-foreground">
              No upcoming renewals or deadlines scheduled on your calendar.
            </p>
          ) : null}
        </div>
      )}
    </Panel>
  );
}

function StatusGroup({
  label,
  items,
  isLoading = false,
}: {
  label: string;
  items: Array<{ status: string; count: number }>;
  isLoading?: boolean;
}) {
  const total = items.reduce((sum, item) => sum + item.count, 0);
  return (
    <div className="border-b border-border/60 px-5 py-4 last:border-b-0">
      <div className="mb-3 flex items-center justify-between text-xs">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">{isLoading ? "Loading…" : `${total} total`}</span>
      </div>
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-4/5" />
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={`${label}-${item.status}`} className="flex items-center gap-3 text-xs">
              <span className="w-24 truncate text-muted-foreground">{item.status}</span>
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
                <span
                  className="block h-full rounded-full bg-jade"
                  style={{ width: `${total ? (item.count / total) * 100 : 0}%` }}
                />
              </span>
              <span className="w-6 text-right tabular-nums">{item.count}</span>
            </div>
          ))}
          {!items.length ? (
            <p className="py-1 text-xs text-muted-foreground">No status data recorded.</p>
          ) : null}
        </div>
      )}
    </div>
  );
}

function Panel({
  title,
  count,
  icon,
  children,
}: {
  title: string;
  count?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="rise overflow-hidden rounded-lg bg-card shadow-hairline">
      <div className="flex items-center gap-2 px-5 py-3.5">
        {icon}
        <h2 className="font-display text-sm font-semibold">{title}</h2>
        {count ? <span className="ml-auto text-xs text-muted-foreground">{count}</span> : null}
      </div>
      <div className="border-t border-border/70">{children}</div>
    </section>
  );
}

function Row({
  title,
  detail,
  value,
  emphasis = false,
}: {
  title: string;
  detail: string;
  value: string;
  emphasis?: boolean;
}) {
  return (
    <div className="flex items-center gap-4 border-b border-border/60 px-5 py-3 last:border-b-0">
      <span className="size-1.5 shrink-0 rounded-full bg-jade" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-[13px] font-medium">{title}</p>
        <p className="truncate text-xs text-muted-foreground">{detail}</p>
      </div>
      <span
        className={
          emphasis ? "text-xs font-medium text-jade" : "text-xs tabular-nums text-muted-foreground"
        }
      >
        {value}
      </span>
    </div>
  );
}

function Empty({ show, text }: { show: boolean; text: string }) {
  return show ? (
    <p className="px-5 py-8 text-center text-sm text-muted-foreground">{text}</p>
  ) : null;
}

function Metric({
  label,
  value,
  isLoading = false,
}: {
  label: string;
  value: number;
  isLoading?: boolean;
}) {
  return (
    <div className="bg-card px-4 py-3">
      <p className="text-muted-foreground">{label}</p>
      {isLoading ? (
        <Skeleton className="mt-1 h-5 w-8" />
      ) : (
        <p className="font-medium text-jade">{value}</p>
      )}
    </div>
  );
}
