import { useState, useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  CheckCircle2,
  Search,
  Filter,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  User,
  Shield,
  Clock,
  Globe,
  Tag,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { activities } from "@/lib/api/resources";

export const Route = createFileRoute("/activity-logs")({ component: ActivityLogs });

function ActivityLogs() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState<string>("all");
  const [selectedRole, setSelectedRole] = useState<string>("all");
  const [selectedAction, setSelectedAction] = useState<string>("all");
  const [selectedDate, setSelectedDate] = useState<string>("");

  const limit = 15;

  // Fetch filter options (users, roles, actions)
  const filterOptionsQuery = useQuery({
    queryKey: ["activities", "filter-options"],
    queryFn: activities.filterOptions,
    staleTime: 60_000,
  });

  // Query paginated and filtered activities from backend PostgreSQL
  const queryParams = useMemo(() => {
    const p: Record<string, unknown> = {
      page,
      limit,
      paginate: true,
    };
    if (search.trim()) p.search = search.trim();
    if (selectedUser !== "all") p.user = selectedUser;
    if (selectedRole !== "all") p.role = selectedRole;
    if (selectedAction !== "all") p.action = selectedAction;
    if (selectedDate) p.date = selectedDate;
    return p;
  }, [page, limit, search, selectedUser, selectedRole, selectedAction, selectedDate]);

  const query = useQuery({
    queryKey: ["activities", queryParams],
    queryFn: () => activities.paginated(queryParams),
    placeholderData: (prev) => prev,
  });

  const filterOptions = filterOptionsQuery.data ?? { users: [], roles: [], actions: [] };
  const items = query.data?.items ?? [];
  const total = query.data?.total ?? 0;
  const totalPages = query.data?.total_pages ?? 1;

  const hasActiveFilters =
    Boolean(search.trim()) ||
    selectedUser !== "all" ||
    selectedRole !== "all" ||
    selectedAction !== "all" ||
    Boolean(selectedDate);

  const handleResetFilters = () => {
    setSearch("");
    setSelectedUser("all");
    setSelectedRole("all");
    setSelectedAction("all");
    setSelectedDate("");
    setPage(1);
  };

  const formatTimestamp = (dateStr?: string | null) => {
    if (!dateStr) return "—";
    try {
      const d = new Date(dateStr);
      return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(d);
    } catch {
      return dateStr;
    }
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-5 py-8 lg:px-8">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <span className="grid size-10 place-items-center rounded-md bg-jade/10 text-jade">
            <Activity className="size-5" />
          </span>
          <div>
            <h1 className="font-display text-2xl font-semibold">Activity timeline</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              A chronological record of contract workspace activity recorded in PostgreSQL.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="px-3 py-1 text-xs">
            {query.isLoading ? "Loading..." : `${total} Total Events`}
          </Badge>
        </div>
      </header>

      {/* Filter and Search Bar */}
      <section className="rounded-lg bg-card p-4 shadow-hairline space-y-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search description, user, action, entity..."
              className="pl-9 text-sm"
            />
          </div>

          {/* User Filter */}
          <div className="w-full lg:w-44">
            <select
              value={selectedUser}
              onChange={(e) => {
                setSelectedUser(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by User"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="all">All Users</option>
              {filterOptions.users.map((u) => (
                <option key={u.id} value={u.name}>
                  {u.name}
                </option>
              ))}
            </select>
          </div>

          {/* Role Filter */}
          <div className="w-full lg:w-40">
            <select
              value={selectedRole}
              onChange={(e) => {
                setSelectedRole(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by Role"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="all">All Roles</option>
              {filterOptions.roles.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {/* Action Filter */}
          <div className="w-full lg:w-44">
            <select
              value={selectedAction}
              onChange={(e) => {
                setSelectedAction(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by Action"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="all">All Actions</option>
              {filterOptions.actions.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>

          {/* Date Filter */}
          <div className="w-full lg:w-36">
            <Input
              type="date"
              value={selectedDate}
              onChange={(e) => {
                setSelectedDate(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by Date"
              className="text-xs"
            />
          </div>

          {/* Reset Filters */}
          {hasActiveFilters && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleResetFilters}
              className="gap-1.5 whitespace-nowrap text-xs"
            >
              <RotateCcw className="size-3.5" />
              Reset
            </Button>
          )}
        </div>
      </section>

      {/* Activity Timeline List */}
      <section className="rounded-lg bg-card p-6 shadow-hairline">
        {query.isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((item) => (
              <Skeleton key={item} className="h-20 w-full" />
            ))}
          </div>
        ) : items.length ? (
          <ol className="space-y-6 border-l-2 border-jade/30 pl-6">
            {items.map((item) => (
              <li key={item.id} className="relative group">
                {/* Node circle */}
                <span className="absolute -left-[34px] grid size-5 place-items-center rounded-full border-2 border-background bg-jade text-white shadow-sm transition-transform group-hover:scale-110">
                  <CheckCircle2 className="size-3" />
                </span>

                <div className="rounded-md border border-border/40 bg-card/60 p-3.5 transition-colors hover:bg-card hover:border-border">
                  {/* Top line: Timestamp, Status, IP */}
                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <Clock className="size-3.5 text-muted-foreground/80" />
                      <span>{formatTimestamp(item.created_at || item.timestamp)}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      {item.status && (
                        <Badge
                          variant={item.status === "Success" ? "secondary" : "destructive"}
                          className="text-[10px] font-normal uppercase tracking-wider py-0 px-1.5"
                        >
                          {item.status}
                        </Badge>
                      )}
                      {item.ip_address && (
                        <span className="flex items-center gap-1 font-mono text-[11px]">
                          <Globe className="size-3 text-muted-foreground/70" />
                          {item.ip_address}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Activity Description */}
                  <p className="mt-2 text-sm font-medium text-foreground">
                    {item.description || item.activity}
                  </p>

                  {/* Metadata Badges */}
                  <div className="mt-2.5 flex flex-wrap items-center gap-2">
                    {/* User & Role Badge */}
                    {item.user_name && (
                      <Badge variant="secondary" className="flex items-center gap-1 text-xs font-normal">
                        <User className="size-3 text-muted-foreground" />
                        <span>{item.user_name}</span>
                        {item.user_role && (
                          <span className="ml-1 text-[10px] text-muted-foreground font-mono">
                            ({item.user_role})
                          </span>
                        )}
                      </Badge>
                    )}

                    {/* Action Badge */}
                    {item.action && (
                      <Badge variant="outline" className="flex items-center gap-1 text-[11px] font-mono">
                        <Tag className="size-3 text-muted-foreground" />
                        {item.action}
                      </Badge>
                    )}

                    {/* Entity Type & ID Badge */}
                    {item.entity_type && (
                      <Badge variant="outline" className="text-[11px]">
                        {item.entity_type} {item.entity_id ? `#${item.entity_id}` : ""}
                      </Badge>
                    )}

                    {/* Contract ID Badge */}
                    {item.contract_id && (
                      <Badge variant="outline" className="text-[11px] text-jade border-jade/30">
                        Contract #{item.contract_id}
                      </Badge>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <div className="py-12 text-center">
            <Filter className="mx-auto size-8 text-muted-foreground/40" />
            <p className="mt-2 text-sm font-medium text-foreground">No activity recorded</p>
            <p className="text-xs text-muted-foreground">
              {hasActiveFilters
                ? "No activity matched your active filter criteria."
                : "Operational activity will automatically appear here as actions occur."}
            </p>
            {hasActiveFilters && (
              <Button variant="outline" size="sm" onClick={handleResetFilters} className="mt-4 text-xs">
                Clear Filters
              </Button>
            )}
          </div>
        )}

        {/* Pagination Controls */}
        {total > 0 && (
          <div className="mt-8 flex flex-col items-center justify-between gap-3 border-t border-border/40 pt-4 sm:flex-row">
            <p className="text-xs text-muted-foreground">
              Showing {(page - 1) * limit + 1}–{Math.min(page * limit, total)} of {total} activities
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1 || query.isFetching}
                className="gap-1 text-xs"
              >
                <ChevronLeft className="size-3.5" />
                Previous
              </Button>
              <span className="px-2 text-xs font-medium">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages || query.isFetching}
                className="gap-1 text-xs"
              >
                Next
                <ChevronRight className="size-3.5" />
              </Button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
