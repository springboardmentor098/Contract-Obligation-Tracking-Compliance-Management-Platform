import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Eye, FileText, Filter, Loader2, Pencil, Search, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  activities,
  compliance,
  contracts,
  obligations,
  renewals,
  users,
} from "@/lib/api/resources";
import { apiErrorMessage } from "@/lib/api/errors";
import type { Contract, User } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/auth-context";
import {
  canAccessRoute,
  canCreateContract,
  canEditContract,
  canDeleteContract,
  canManageUsers,
} from "@/lib/auth/rbac-permissions";

export const Route = createFileRoute("/contracts")({ component: ContractsPage });

function ContractsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const allowCreate = canCreateContract(user?.role);
  const allowEdit = canEditContract(user?.role);
  const allowDelete = canDeleteContract(user?.role);
  const allowUsers = canManageUsers(user?.role);
  const allowCompliance = canAccessRoute("/compliance", user?.role);

  const [form, setForm] = useState({
    title: "",
    contract_number: "",
    category: "",
    department: "",
    assigned_to: "",
    start_date: "",
    end_date: "",
    description: "",
  });
  const [busy, setBusy] = useState(false);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({
    status: "",
    category: "",
    department: "",
    manager: "",
    risk: "",
    endDate: "",
  });
  const [detailId, setDetailId] = useState<number | null>(null);
  const [openInEditMode, setOpenInEditMode] = useState(false);
  const contractQuery = useQuery({ queryKey: ["contracts"], queryFn: contracts.list });
  const usersQuery = useQuery({
    queryKey: ["users"],
    queryFn: users.list,
    enabled: allowUsers,
  });
  const complianceQuery = useQuery({
    queryKey: ["compliance"],
    queryFn: compliance.list,
    enabled: allowCompliance,
  });
  const categories = [...new Set((contractQuery.data ?? []).map((item) => item.category))];
  const departments = [
    ...new Set((contractQuery.data ?? []).map((item) => item.department).filter(Boolean)),
  ] as string[];
  const managerName = (id: number | null) =>
    usersQuery.data?.find((user) => user.id === id)?.full_name ?? "Unassigned";
  const categoryOptions = [
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement",
  ];
  const filtered = useMemo(() => {
    const query = search.toLowerCase();
    return (contractQuery.data ?? []).filter(
      (item) =>
        [item.title, item.contract_number, item.category, item.department ?? "", managerName(item.assigned_to)]
          .join(" ")
          .toLowerCase()
          .includes(query) &&
        (!filters.status || item.status === filters.status) &&
        (!filters.category || item.category === filters.category) &&
        (!filters.department || item.department === filters.department) &&
        (!filters.manager || String(item.assigned_to) === filters.manager) &&
        (!filters.risk ||
          complianceQuery.data?.find((entry) => entry.contract_id === item.id)?.risk_level ===
            filters.risk) &&
        (!filters.endDate || item.end_date <= filters.endDate),
    );
  }, [complianceQuery.data, contractQuery.data, filters, search, usersQuery.data]);

  const openDetails = (id: number, edit = false) => {
    setOpenInEditMode(edit);
    setDetailId(id);
  };
  const removeContract = async (contract: Contract) => {
    if (!window.confirm("Delete Contract?\n\nThis action cannot be undone.")) return;
    try {
      queryClient.setQueryData<Contract[]>(["contracts"], (current) =>
        current?.filter((item) => item.id !== contract.id),
      );
      await contracts.delete(contract.id);
      await queryClient.invalidateQueries({ queryKey: ["contracts"] });
      toast.success("Contract deleted successfully.");
    } catch (error) {
      await queryClient.invalidateQueries({ queryKey: ["contracts"] });
      toast.error(apiErrorMessage(error, "Unable to delete contract."));
    }
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (
      !form.title.trim() ||
      !form.contract_number.trim() ||
      !form.category ||
      !form.start_date ||
      !form.end_date ||
      !form.description.trim()
    ) {
      toast.error("Complete all required contract fields.");
      return;
    }
    if (form.end_date < form.start_date) {
      toast.error("End date must be on or after start date.");
      return;
    }
    setBusy(true);
    try {
      await contracts.create({
        title: form.title.trim(),
        contract_number: form.contract_number.trim(),
        category: form.category,
        department: form.department.trim() || null,
        assigned_to: form.assigned_to ? Number(form.assigned_to) : null,
        start_date: form.start_date,
        end_date: form.end_date,
        description: form.description.trim(),
      });
      setForm({
        title: "",
        contract_number: "",
        category: "",
        department: "",
        assigned_to: "",
        start_date: "",
        end_date: "",
        description: "",
      });
      await queryClient.invalidateQueries({ queryKey: ["contracts"] });
      toast.success("Contract created");
    } catch (error) {
      toast.error(apiErrorMessage(error, "Unable to create contract."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-5 py-8 lg:px-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex items-start gap-4">
          <span className="grid size-10 place-items-center rounded-md bg-jade/10 text-jade">
            <FileText className="size-5" />
          </span>
          <div>
            <h1 className="font-display text-2xl font-semibold">Contracts</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Search contracts and move them through review.
            </p>
          </div>
        </div>
        <label className="flex h-9 items-center gap-2 rounded-md bg-secondary px-3 text-sm">
          <Search className="size-4 text-muted-foreground" />
          <input
            className="w-56 bg-transparent outline-none"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search title, number, owner…"
          />
        </label>
      </header>
      {allowCreate && (
        <section className="rounded-lg bg-card p-5 shadow-hairline">
          <h2 className="mb-4 font-display text-sm font-semibold">Create Contract</h2>
          <form className="grid gap-4 md:grid-cols-4" onSubmit={submit}>
            <CreateField
              label="Title"
              value={form.title}
              onChange={(value) => setForm({ ...form, title: value })}
            />
            <CreateField
              label="Contract Number"
              value={form.contract_number}
              onChange={(value) => setForm({ ...form, contract_number: value })}
            />
            <CreateSelect
              label="Category"
              value={form.category}
              options={categoryOptions}
              onChange={(value) => setForm({ ...form, category: value })}
            />
            <CreateField
              label="Department"
              required={false}
              value={form.department}
              onChange={(value) => setForm({ ...form, department: value })}
            />
            <CreateSelect
              label="Manager"
              required={false}
              value={form.assigned_to}
              options={(usersQuery.data ?? []).map((user) => ({
                value: String(user.id),
                label: user.full_name,
              }))}
              onChange={(value) => setForm({ ...form, assigned_to: value })}
            />
            <CreateField
              label="Start Date"
              type="date"
              value={form.start_date}
              onChange={(value) => setForm({ ...form, start_date: value })}
            />
            <CreateField
              label="End Date"
              type="date"
              value={form.end_date}
              onChange={(value) => setForm({ ...form, end_date: value })}
            />
            <label className="space-y-2 text-sm md:col-span-4">
              <Label>Description</Label>
              <Textarea
                required
                value={form.description}
                onChange={(event) => setForm({ ...form, description: event.target.value })}
              />
            </label>
            <div className="md:col-span-4">
              <Button type="submit" disabled={busy}>
                {busy ? "Creating…" : "Create Contract"}
              </Button>
            </div>
          </form>
        </section>
      )}
      <section className="grid gap-6 lg:grid-cols-[220px_1fr]">
        <aside className="rounded-lg border border-border bg-card p-4 shadow-hairline">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Filter className="size-4" />
            Filters
          </div>
          <div className="space-y-3">
            <FilterSelect
              label="Status"
              value={filters.status}
              options={["Draft", "Under Review", "Approved", "Active", "Expired", "Terminated"]}
              onChange={(value) => setFilters({ ...filters, status: value })}
            />
            <FilterSelect
              label="Category"
              value={filters.category}
              options={categories}
              onChange={(value) => setFilters({ ...filters, category: value })}
            />
            <FilterSelect
              label="Department"
              value={filters.department}
              options={departments}
              onChange={(value) => setFilters({ ...filters, department: value })}
            />
            <FilterSelect
              label="Manager"
              value={filters.manager}
              options={(usersQuery.data ?? []).map((user) => String(user.id))}
              labels={(usersQuery.data ?? []).map((user) => user.full_name)}
              onChange={(value) => setFilters({ ...filters, manager: value })}
            />
            <FilterSelect
              label="Risk level"
              value={filters.risk}
              options={["High", "Medium", "Low"]}
              onChange={(value) => setFilters({ ...filters, risk: value })}
            />
            <label className="space-y-1 text-xs text-muted-foreground">
              End date
              <input
                type="date"
                className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground"
                value={filters.endDate}
                onChange={(event) => setFilters({ ...filters, endDate: event.target.value })}
              />
            </label>
          </div>
        </aside>
        <section className="overflow-x-auto rounded-lg bg-card shadow-hairline">
          {contractQuery.isLoading ? (
              <div className="grid min-h-40 place-items-center"><Loader2 className="size-6 animate-spin text-jade" /></div>
          ) : contractQuery.isError ? (
            <p className="p-10 text-center text-sm text-destructive">Unable to load contracts.</p>
          ) : filtered.length === 0 ? (
            <div className="p-14 text-center">
              <FileText className="mx-auto size-9 text-muted-foreground" />
              <h2 className="mt-3 font-display text-lg font-semibold">No contracts yet</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Create a contract to start tracking its lifecycle.
              </p>
            </div>
          ) : (
            <table className="w-full min-w-[1180px] text-left text-sm">
              <thead className="sticky top-0 z-10 bg-secondary/95">
                <tr className="border-b border-border text-xs text-muted-foreground">
                  <th className="px-4 py-3">Contract Name</th>
                  <th className="px-4 py-3">Contract Number</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Manager</th>
                  <th className="px-4 py-3">Start Date</th>
                  <th className="px-4 py-3">End Date</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item, index) => (
                  <tr
                    key={item.id}
                    className={`border-b border-border/60 transition-colors hover:bg-jade/5 ${index % 2 ? "bg-secondary/20" : "bg-card"}`}
                  >
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        className="font-semibold text-jade hover:underline"
                        onClick={() => openDetails(item.id)}
                      >
                        {item.title}
                      </button>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">{item.contract_number}</td>
                    <td className="px-4 py-3">{item.category}</td>
                    <td className="px-4 py-3">{item.department || "—"}</td>
                    <td className="px-4 py-3">
                      {usersQuery.data?.find((user) => user.id === item.assigned_to)?.full_name ||
                        "Unassigned"}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">{item.start_date}</td>
                    <td className="px-4 py-3 whitespace-nowrap">{item.end_date}</td>
                    <td className="px-4 py-3">
                      <StatusChip status={item.status} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <Button
                          size="icon"
                          variant="ghost"
                          title="View"
                          aria-label="View contract"
                          onClick={() => openDetails(item.id)}
                        >
                          <Eye className="size-4" />
                        </Button>
                        {allowEdit && (
                          <Button
                            size="icon"
                            variant="ghost"
                            title="Edit"
                            aria-label="Edit contract"
                            onClick={() => openDetails(item.id, true)}
                          >
                            <Pencil className="size-4" />
                          </Button>
                        )}
                        {allowDelete && (
                          <Button
                            size="icon"
                            variant="ghost"
                            title="Delete"
                            aria-label="Delete contract"
                            onClick={() => removeContract(item)}
                          >
                            <Trash2 className="size-4 text-destructive" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </section>
      <ContractDetailsDialog
        contractId={detailId}
        open={detailId !== null}
        initialEdit={openInEditMode}
        users={usersQuery.data ?? []}
        userRole={user?.role}
        onClose={() => setDetailId(null)}
        onUpdated={async () => {
          setOpenInEditMode(false);
          await queryClient.invalidateQueries({ queryKey: ["contracts"] });
        }}
        onDeleted={async () => {
          setDetailId(null);
          await queryClient.invalidateQueries({ queryKey: ["contracts"] });
        }}
      />
    </main>
  );
}

function ContractDetailsDialog({
  contractId,
  open,
  initialEdit,
  users: userList,
  userRole,
  onClose,
  onUpdated,
  onDeleted,
}: {
  contractId: number | null;
  open: boolean;
  initialEdit: boolean;
  users: User[];
  userRole?: string | null;
  onClose: () => void;
  onUpdated: () => Promise<void>;
  onDeleted: () => Promise<void>;
}) {
  const queryClient = useQueryClient();
  const allowObligations = canAccessRoute("/obligations", userRole);
  const allowRenewals = canAccessRoute("/renewals", userRole);
  const allowCompliance = canAccessRoute("/compliance", userRole);
  const allowActivities = canAccessRoute("/activities", userRole);
  const allowEdit = canEditContract(userRole);
  const allowDelete = canDeleteContract(userRole);

  const contract = useQuery({
    queryKey: ["contract", contractId],
    queryFn: () => contracts.get(contractId as number),
    enabled: open && contractId !== null,
  });
  const obligationList = useQuery({
    queryKey: ["obligations", "contract", contractId],
    queryFn: () => obligations.forContract(contractId as number),
    enabled: open && contractId !== null && allowObligations,
  });
  const renewalList = useQuery({
    queryKey: ["renewals", "contract", contractId],
    queryFn: () => renewals.forContract(contractId as number),
    enabled: open && contractId !== null && allowRenewals,
  });
  const complianceResult = useQuery({
    queryKey: ["compliance", "contract", contractId],
    queryFn: () => compliance.byContract(contractId as number),
    enabled: open && contractId !== null && allowCompliance,
  });
  const activityList = useQuery({
    queryKey: ["activities", "contract", contractId],
    queryFn: async () =>
      (await activities.list()).filter((entry) => entry.contract_id === contractId),
    enabled: open && contractId !== null && allowActivities,
  });
  const [editMode, setEditMode] = useState(initialEdit);
  const [saving, setSaving] = useState(false);
  const [editForm, setEditForm] = useState({
    title: "",
    contract_number: "",
    category: "",
    department: "",
    assigned_to: "",
    start_date: "",
    end_date: "",
    description: "",
  });
  const item = contract.data;
  const manager = userList.find((user) => user.id === item?.assigned_to);
  const latestActivity = [...(activityList.data ?? [])].sort((a, b) =>
    String(b.created_at ?? "").localeCompare(String(a.created_at ?? "")),
  )[0];

  useEffect(() => {
    setEditMode(initialEdit);
    if (item)
      setEditForm({
        title: item.title,
        contract_number: item.contract_number,
        category: item.category,
        department: item.department ?? "",
        assigned_to: item.assigned_to ? String(item.assigned_to) : "",
        start_date: item.start_date,
        end_date: item.end_date,
        description: item.description,
      });
  }, [initialEdit, item]);

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (
      !item ||
      !editForm.title.trim() ||
      !editForm.contract_number.trim() ||
      !editForm.category ||
      !editForm.start_date ||
      !editForm.end_date ||
      !editForm.description.trim()
    ) {
      toast.error("Complete all required contract fields.");
      return;
    }
    if (editForm.end_date < editForm.start_date) {
      toast.error("End date must be on or after start date.");
      return;
    }
    setSaving(true);
    try {
      await contracts.update(item.id, {
        ...editForm,
        title: editForm.title.trim(),
        contract_number: editForm.contract_number.trim(),
        department: editForm.department.trim() || null,
        assigned_to: editForm.assigned_to ? Number(editForm.assigned_to) : null,
        description: editForm.description.trim(),
      });
      await queryClient.invalidateQueries({ queryKey: ["contract", item.id] });
      await onUpdated();
      setEditMode(false);
      toast.success("Contract updated successfully.");
    } catch (error) {
      toast.error(apiErrorMessage(error, "Unable to update contract."));
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!item || !window.confirm("Delete Contract?\n\nThis action cannot be undone.")) return;
    try {
      await contracts.delete(item.id);
      await onDeleted();
      toast.success("Contract deleted successfully.");
    } catch (error) {
      toast.error(apiErrorMessage(error, "Unable to delete contract."));
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(nextOpen) => {
        if (!nextOpen && !saving) onClose();
      }}
    >
      <DialogContent className="flex max-h-[90vh] min-h-0 max-w-4xl flex-col gap-0 overflow-hidden rounded-xl p-0">
        <DialogHeader className="sticky top-0 z-10 border-b border-border bg-background px-6 py-5">
          <DialogTitle>
            {editMode ? "Edit Contract" : "Contract Details"}
            {!editMode && item ? <span className="mt-2 block text-sm font-normal text-muted-foreground">{item.contract_number}</span> : null}
          </DialogTitle>
        </DialogHeader>
        {contract.isLoading ? (
          <div className="grid min-h-64 place-items-center px-6 py-8">
            <Loader2 className="size-7 animate-spin text-jade" />
          </div>
        ) : contract.isError || !item ? (
          <div className="px-6 py-10 text-center"><p className="font-medium text-destructive">Unable to load contract details.</p><p className="mt-2 text-sm text-muted-foreground">Please try again later.</p></div>
        ) : editMode ? (
          <form className="grid min-h-0 flex-1 gap-4 overflow-y-auto px-6 py-6 md:grid-cols-2" onSubmit={save}>
            <CreateField
              label="Title"
              value={editForm.title}
              onChange={(value) => setEditForm({ ...editForm, title: value })}
            />
            <CreateField
              label="Contract Number"
              value={editForm.contract_number}
              onChange={(value) => setEditForm({ ...editForm, contract_number: value })}
            />
            <CreateSelect
              label="Category"
              value={editForm.category}
              options={categoryOptions}
              onChange={(value) => setEditForm({ ...editForm, category: value })}
            />
            <CreateField
              label="Department"
              required={false}
              value={editForm.department}
              onChange={(value) => setEditForm({ ...editForm, department: value })}
            />
            <CreateSelect
              label="Manager"
              required={false}
              value={editForm.assigned_to}
              options={userList.map((user) => ({ value: String(user.id), label: user.full_name }))}
              onChange={(value) => setEditForm({ ...editForm, assigned_to: value })}
            />
            <CreateField
              label="Start Date"
              type="date"
              value={editForm.start_date}
              onChange={(value) => setEditForm({ ...editForm, start_date: value })}
            />
            <CreateField
              label="End Date"
              type="date"
              value={editForm.end_date}
              onChange={(value) => setEditForm({ ...editForm, end_date: value })}
            />
            <label className="space-y-2 text-sm md:col-span-2">
              <Label>Description</Label>
              <Textarea
                required
                value={editForm.description}
                onChange={(event) => setEditForm({ ...editForm, description: event.target.value })}
              />
            </label>
            <DialogFooter className="sticky bottom-0 -mx-6 -mb-6 border-t border-border bg-background px-6 py-4 md:col-span-2">
              <Button type="button" variant="ghost" onClick={onClose} disabled={saving}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save"}
              </Button>
            </DialogFooter>
          </form>
        ) : (
          <div className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
            <div className="grid gap-5 md:grid-cols-2">
              <InfoSection title="Contract information"><Info label="Title" value={item.title} /><Info label="Contract Number" value={item.contract_number} /><Info label="Category" value={item.category} /><Info label="Department" value={item.department || "Unassigned"} /><Info label="Manager" value={manager?.full_name || "Unassigned"} /><Info label="Status" value={<StatusChip status={item.status} />} /></InfoSection>
              <InfoSection title="Dates and ownership"><Info label="Start Date" value={item.start_date} /><Info label="End Date" value={item.end_date} /><Info label="Created Date" value={formatDate(item.created_at)} /><Info label="Last Updated" value={formatDate(item.updated_at)} /><Info label="Assigned User" value={manager ? `${manager.full_name} · ${manager.role}` : "None"} /><Info label="Compliance Status" value={complianceResult.data?.status ?? "Unavailable"} /><Info label="Risk Level" value={complianceResult.data?.risk_level ?? "Unavailable"} /></InfoSection>
              <InfoSection title="Description" className="md:col-span-2"><p className="whitespace-pre-wrap text-sm leading-6">{item.description || "No description provided."}</p></InfoSection>
              <InfoSection title="Obligations"><div className="grid grid-cols-3 gap-3"><Metric label="Total" value={obligationList.data?.length ?? 0} /><Metric label="Completed" value={obligationList.data?.filter((entry) => entry.status === "Completed").length ?? 0} /><Metric label="Pending" value={obligationList.data?.filter((entry) => entry.status !== "Completed").length ?? 0} /></div></InfoSection>
              <InfoSection title="Renewals"><Info label="Renewal Date" value={renewalList.data?.[0]?.renewal_date ?? "None"} /><Info label="Renewal Status" value={renewalList.data?.[0]?.status ?? "None"} /></InfoSection>
              <InfoSection title="Activity" className="md:col-span-2"><Info label="Latest Activity" value={latestActivity?.activity ?? "No activity recorded"} /></InfoSection>
            </div>
            <DialogFooter className="sticky bottom-[-1.5rem] mt-6 -mx-6 -mb-6 border-t border-border bg-background px-6 py-4">
              <Button variant="ghost" onClick={onClose}>
                Close
              </Button>
              {allowDelete && (
                <Button variant="outline" onClick={remove}>
                  <Trash2 className="mr-2 size-4 text-destructive" />
                  Delete Contract
                </Button>
              )}
              {allowEdit && (
                <Button onClick={() => setEditMode(true)}>
                  <Pencil className="mr-2 size-4" />
                  Edit Contract
                </Button>
              )}
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
function Info({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="border-b border-border/60 pb-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
      <div className="mt-1 text-sm font-medium">{value}</div>
    </div>
  );
}
function InfoSection({ title, children, className = "" }: { title: string; children: React.ReactNode; className?: string }) {
  return <section className={`rounded-lg border border-border bg-card p-4 shadow-hairline ${className}`}><h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{title}</h3><div className="grid gap-4 sm:grid-cols-2">{children}</div></section>;
}
function Metric({ label, value }: { label: string; value: number }) {
  return <div className="rounded-md bg-secondary/70 p-3"><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 font-display text-xl font-semibold">{value}</p></div>;
}
function StatusChip({ status }: { status: string }) {
  const colors: Record<string, string> = {
    Draft: "bg-slate-100 text-slate-700",
    "Under Review": "bg-orange-100 text-orange-800",
    Approved: "bg-blue-100 text-blue-800",
    Active: "bg-emerald-100 text-emerald-800",
    Expired: "bg-red-100 text-red-800",
    Terminated: "bg-slate-700 text-white",
  };
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${colors[status] ?? "bg-secondary text-foreground"}`}
    >
      {status}
    </span>
  );
}
function CreateField({
  label,
  value,
  onChange,
  type = "text",
  required = true,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="space-y-2 text-sm">
      <Label>{label}</Label>
      <Input
        type={type}
        required={required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
function CreateSelect({
  label,
  value,
  options,
  onChange,
  required = true,
}: {
  label: string;
  value: string;
  options: (string | { value: string; label: string })[];
  onChange: (value: string) => void;
  required?: boolean;
}) {
  return (
    <label className="space-y-2 text-sm">
      <Label>{label}</Label>
      <select
        className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
        required={required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">Select…</option>
        {options.map((option) =>
          typeof option === "string" ? (
            <option key={option}>{option}</option>
          ) : (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ),
        )}
      </select>
    </label>
  );
}
function FilterSelect({
  label,
  value,
  options,
  labels = options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  labels?: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="space-y-1 text-xs text-muted-foreground">
      {label}
      <select
        className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">All</option>
        {options.map((option, index) => (
          <option key={option} value={option}>
            {labels[index] ?? option}
          </option>
        ))}
      </select>
    </label>
  );
}
