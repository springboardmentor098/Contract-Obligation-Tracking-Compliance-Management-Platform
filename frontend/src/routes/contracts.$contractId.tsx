import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Check, FileText, Pencil, Play, Plus, Send, ShieldCheck, Archive } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { activities, compliance, contracts, obligations, renewals, users } from "@/lib/api/resources";
import { apiErrorMessage } from "@/lib/api/errors";
import { useAuth } from "@/lib/auth/auth-context";
import {
  canAccessRoute,
  canApproveContract,
  canEditContract,
  canManageUsers,
  canSubmitContractReview,
} from "@/lib/auth/rbac-permissions";
import type { Contract } from "@/lib/api/types";

export const Route = createFileRoute("/contracts/$contractId")({ component: ContractDetails });

function ContractDetails() {
  const { user } = useAuth();
  const id = Number(Route.useParams().contractId);
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [addingObligation, setAddingObligation] = useState(false);

  const allowEdit = canEditContract(user?.role);
  const allowApprove = canApproveContract(user?.role);
  const allowSubmitReview = canSubmitContractReview(user?.role);
  const allowUsers = canManageUsers(user?.role);
  const allowObligations = canAccessRoute("/obligations", user?.role);
  const allowRenewals = canAccessRoute("/renewals", user?.role);
  const allowCompliance = canAccessRoute("/compliance", user?.role);
  const allowActivities = canAccessRoute("/activities", user?.role);

  const contract = useQuery({ queryKey: ["contracts", id], queryFn: () => contracts.get(id), enabled: id > 0 });
  const usersQuery = useQuery({ queryKey: ["users"], queryFn: users.list, enabled: allowUsers });
  const obligationList = useQuery({
    queryKey: ["obligations", "contract", id],
    queryFn: () => obligations.forContract(id),
    enabled: contract.isSuccess && allowObligations,
  });
  const renewalList = useQuery({
    queryKey: ["renewals", "contract", id],
    queryFn: () => renewals.forContract(id),
    enabled: contract.isSuccess && allowRenewals,
  });
  const complianceResult = useQuery({
    queryKey: ["compliance", "contract", id],
    queryFn: () => compliance.byContract(id),
    enabled: contract.isSuccess && allowCompliance,
  });
  const activityList = useQuery({
    queryKey: ["activities", id],
    queryFn: async () => (await activities.list()).filter((item) => item.contract_id === id),
    enabled: contract.isSuccess && allowActivities,
  });

  if (contract.isLoading) return <main className="mx-auto max-w-7xl px-5 py-8 text-sm text-muted-foreground">Loading contract…</main>;
  if (contract.isError || !contract.data) return <main className="mx-auto max-w-7xl px-5 py-8 text-sm text-destructive">{apiErrorMessage(contract.error, "Unable to load this contract.")}</main>;
  const item = contract.data;
  const manager = usersQuery.data?.find((u) => u.id === item.assigned_to);

  const save = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!allowEdit) return;
    setSaving(true);
    const form = new FormData(event.currentTarget);
    try {
      await contracts.update(id, {
        title: form.get("title"),
        description: form.get("description"),
        category: form.get("category"),
        start_date: form.get("start_date"),
        end_date: form.get("end_date"),
        department: form.get("department"),
        assigned_to: form.get("assigned_to") ? Number(form.get("assigned_to")) : null,
      });
      setEditing(false);
      await queryClient.invalidateQueries({ queryKey: ["contracts", id] });
      await queryClient.invalidateQueries({ queryKey: ["contracts"] });
      toast.success("Contract updated");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to update contract.");
    } finally {
      setSaving(false);
    }
  };

  const transition = async (status: string) => {
    try {
      await contracts.transition(id, status);
      await queryClient.invalidateQueries({ queryKey: ["contracts", id] });
      await queryClient.invalidateQueries({ queryKey: ["contracts"] });
      toast.success(`Contract ${status.toLowerCase()}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to change contract status.");
    }
  };

  const completeObligation = async (obligationId: number) => {
    try {
      await obligations.status(obligationId, "Completed");
      await queryClient.invalidateQueries({ queryKey: ["obligations", "contract", id] });
      await queryClient.invalidateQueries({ queryKey: ["obligations"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Obligation completed");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to complete obligation.");
    }
  };

  // Determine allowed transition actions based on user role
  const rawActions: Record<string, { label: string; next: string; icon: typeof Send; requiresApprove?: boolean; requiresSubmit?: boolean }[]> = {
    Draft: [{ label: "Submit review", next: "Under Review", icon: Send, requiresSubmit: true }],
    "Under Review": [{ label: "Approve", next: "Approved", icon: ShieldCheck, requiresApprove: true }],
    Approved: [{ label: "Activate", next: "Active", icon: Play, requiresApprove: true }],
    Active: [{ label: "Terminate", next: "Terminated", icon: Archive, requiresApprove: true }],
    Terminated: [{ label: "Archive", next: "Archived", icon: Archive, requiresApprove: true }],
  };

  const availableActions = (rawActions[item.status] ?? []).filter((action) => {
    if (action.requiresApprove && !allowApprove) return false;
    if (action.requiresSubmit && !allowSubmitReview) return false;
    return true;
  });

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-5 py-8 lg:px-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-4">
          <span className="grid size-10 place-items-center rounded-md bg-jade/10 text-jade">
            <FileText className="size-5" />
          </span>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Contract {item.contract_number}</p>
            <h1 className="font-display text-2xl font-semibold">{item.title}</h1>
            <p className="mt-1 text-sm text-muted-foreground">{item.status} · {item.category}{item.department ? ` · ${item.department}` : ""}</p>
          </div>
        </div>

        {/* Action Buttons: hidden for read-only roles */}
        <div className="flex flex-wrap gap-2">
          {availableActions.map((action) => (
            <Button
              key={action.next}
              size="sm"
              variant={action.next === "Approved" ? "approve" : "outline"}
              onClick={() => transition(action.next)}
            >
              <action.icon className="mr-2 size-4" />
              {action.label}
            </Button>
          ))}
          {allowEdit && (
            <Button size="sm" variant="outline" onClick={() => setEditing((value) => !value)}>
              <Pencil className="mr-2 size-4" />
              {editing ? "Cancel" : "Edit"}
            </Button>
          )}
        </div>
      </header>

      {editing && allowEdit ? <EditForm contract={item} users={usersQuery.data ?? []} saving={saving} onSubmit={save} /> : null}

      <Tabs defaultValue="overview" className="space-y-5">
        <TabsList className="flex h-auto flex-wrap justify-start gap-1 bg-secondary p-1">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          {allowObligations && <TabsTrigger value="obligations">Obligations</TabsTrigger>}
          {allowRenewals && <TabsTrigger value="renewals">Renewals</TabsTrigger>}
          {allowCompliance && <TabsTrigger value="compliance">Compliance</TabsTrigger>}
          {allowActivities && <TabsTrigger value="activity">Activity</TabsTrigger>}
        </TabsList>

        <TabsContent value="overview">
          <Panel title="Overview">
            <dl className="grid gap-5 text-sm sm:grid-cols-2 lg:grid-cols-3">
              <Detail label="Title" value={item.title} />
              <Detail label="Category" value={item.category} />
              <Detail label="Department" value={item.department || "Unassigned"} />
              <Detail label="Assigned manager" value={manager?.full_name || "Unassigned"} />
              <Detail label="Start date" value={item.start_date} />
              <Detail label="End date" value={item.end_date} />
              <Detail label="Description" value={item.description} />
            </dl>
          </Panel>
        </TabsContent>

        {allowObligations && (
          <TabsContent value="obligations">
            <Panel title="Obligations">
              {allowEdit && (
                <div className="mb-4 flex justify-end">
                  <Button size="sm" onClick={() => setAddingObligation((value) => !value)}>
                    <Plus className="mr-2 size-4" />Add obligation
                  </Button>
                </div>
              )}
              {addingObligation && allowEdit ? (
                <QuickObligationForm
                  contractId={id}
                  users={usersQuery.data ?? []}
                  onSaved={async () => {
                    setAddingObligation(false);
                    await queryClient.invalidateQueries({ queryKey: ["obligations", "contract", id] });
                    await queryClient.invalidateQueries({ queryKey: ["obligations"] });
                    await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
                    toast.success("Obligation created");
                  }}
                />
              ) : null}
              {obligationList.isLoading ? (
                <p className="text-sm text-muted-foreground">Loading…</p>
              ) : obligationList.data?.length ? (
                <ul className="space-y-3">
                  {obligationList.data.map((entry) => (
                    <li key={entry.id} className="flex items-center justify-between gap-3 border-b border-border/60 pb-3 last:border-0">
                      <div>
                        <p className="font-medium">{entry.title}</p>
                        <p className="text-xs text-muted-foreground">
                          Due {entry.due_date} · Assigned {usersQuery.data?.find((u) => u.id === entry.assigned_to)?.full_name ?? "Unassigned"} · {entry.priority ?? "Medium"}
                        </p>
                      </div>
                      {entry.status !== "Completed" && allowEdit ? (
                        <Button size="sm" variant="approve" onClick={() => completeObligation(entry.id)}>
                          <Check className="mr-2 size-4" />Complete
                        </Button>
                      ) : (
                        <span className="text-xs text-jade font-medium">{entry.status}</span>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <Empty text="No obligations found." />
              )}
            </Panel>
          </TabsContent>
        )}

        {allowRenewals && (
          <TabsContent value="renewals">
            <ListPanel
              title="Renewals"
              items={(renewalList.data ?? []).map((entry) => `${entry.renewal_date} → ${entry.new_expiry_date} · ${entry.status}`)}
              loading={renewalList.isLoading}
            />
          </TabsContent>
        )}

        {allowCompliance && (
          <TabsContent value="compliance">
            <Panel title="Compliance">
              {complianceResult.data ? (
                <dl className="grid gap-5 text-sm sm:grid-cols-3">
                  <Detail label="Status" value={complianceResult.data.status} />
                  <Detail label="Risk level" value={complianceResult.data.risk_level} />
                  <Detail label="Score" value={String(complianceResult.data.compliance_score)} />
                </dl>
              ) : (
                <Empty text="No compliance record found." />
              )}
            </Panel>
          </TabsContent>
        )}

        {allowActivities && (
          <TabsContent value="activity">
            <ListPanel
              title="Activity history"
              items={(activityList.data ?? []).map((entry) => entry.activity)}
              loading={activityList.isLoading}
            />
          </TabsContent>
        )}
      </Tabs>
    </main>
  );
}

function EditForm({ contract, users, saving, onSubmit }: { contract: Contract; users: { id: number; full_name: string; role: string }[]; saving: boolean; onSubmit: (event: React.FormEvent<HTMLFormElement>) => void }) {
  return (
    <form className="grid gap-4 rounded-lg bg-card p-5 shadow-hairline md:grid-cols-2" onSubmit={onSubmit}>
      <Field name="title" label="Title" defaultValue={contract.title} />
      <Field name="category" label="Category" defaultValue={contract.category} />
      <Field name="department" label="Department" defaultValue={contract.department ?? ""} />
      <label className="space-y-2 text-sm">
        <Label>Assigned manager</Label>
        <select name="assigned_to" defaultValue={contract.assigned_to ?? ""} className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm">
          <option value="">Unassigned</option>
          {users.map((user) => <option key={user.id} value={user.id}>{user.full_name} · {user.role}</option>)}
        </select>
      </label>
      <Field name="start_date" label="Start date" type="date" defaultValue={contract.start_date} />
      <Field name="end_date" label="End date" type="date" defaultValue={contract.end_date} />
      <label className="space-y-2 text-sm md:col-span-2">
        <Label>Description</Label>
        <Textarea name="description" required defaultValue={contract.description} />
      </label>
      <Button type="submit" disabled={saving} className="md:w-fit">
        {saving ? "Saving…" : "Save changes"}
      </Button>
    </form>
  );
}

function Field({ name, label, defaultValue, type = "text" }: { name: string; label: string; defaultValue: string; type?: string }) {
  return <label className="space-y-2 text-sm"><Label>{label}</Label><Input name={name} required defaultValue={defaultValue} type={type} /></label>;
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rise rounded-lg bg-card p-5 shadow-hairline"><h2 className="mb-5 font-display text-sm font-semibold">{title}</h2>{children}</section>;
}

function Detail({ label, value }: { label: string; value: string }) {
  return <div><dt className="text-muted-foreground">{label}</dt><dd className="mt-1 font-medium">{value}</dd></div>;
}

function ListPanel({ title, items, loading }: { title: string; items: string[]; loading: boolean }) {
  return <Panel title={title}>{loading ? <p className="text-sm text-muted-foreground">Loading…</p> : items.length ? <ul className="space-y-2 text-sm">{items.map((item, index) => <li key={`${title}-${index}`} className="border-b border-border/60 pb-2 last:border-0">{item}</li>)}</ul> : <Empty text={`No ${title.toLowerCase()} found.`} />}</Panel>;
}

function Empty({ text }: { text: string }) {
  return <p className="text-sm text-muted-foreground">{text}</p>;
}

function QuickObligationForm({ contractId, users, onSaved }: { contractId: number; users: { id: number; full_name: string; role: string }[]; onSaved: () => Promise<void> }) {
  const [saving, setSaving] = useState(false);
  const save = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    const form = new FormData(event.currentTarget);
    try {
      await obligations.create({
        contract_id: contractId,
        title: form.get("title"),
        description: form.get("description"),
        obligation_type: form.get("obligation_type"),
        priority: form.get("priority"),
        due_date: form.get("due_date"),
        assigned_to: Number(form.get("assigned_to")),
      });
      await onSaved();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to create obligation.");
    } finally {
      setSaving(false);
    }
  };
  return (
    <form className="mb-5 grid gap-3 rounded-md border border-border p-4 md:grid-cols-2" onSubmit={save}>
      <Field name="title" label="Title" defaultValue="" />
      <Field name="obligation_type" label="Type" defaultValue="" />
      <Field name="due_date" label="Due date" type="date" defaultValue="" />
      <label className="space-y-2 text-sm">
        <Label>Priority</Label>
        <select name="priority" defaultValue="Medium" className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm">
          <option>Low</option>
          <option>Medium</option>
          <option>High</option>
          <option>Critical</option>
        </select>
      </label>
      <label className="space-y-2 text-sm">
        <Label>Assigned employee</Label>
        <select name="assigned_to" required className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm">
          <option value="">Select…</option>
          {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
        </select>
      </label>
      <label className="space-y-2 text-sm md:col-span-2">
        <Label>Description</Label>
        <Textarea name="description" required />
      </label>
      <Button type="submit" disabled={saving} className="md:w-fit">
        {saving ? "Saving…" : "Create obligation"}
      </Button>
    </form>
  );
}
