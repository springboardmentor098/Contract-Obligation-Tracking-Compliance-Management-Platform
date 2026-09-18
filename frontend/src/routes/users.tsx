import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  CheckCircle2,
  KeyRound,
  Search,
  Shield,
  Trash2,
  UserCheck,
  UserX,
  UsersRound,
} from "lucide-react";
import { toast } from "sonner";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/lib/auth/auth-context";
import { ROLES, normalizeRole } from "@/lib/auth/rbac-permissions";
import { users } from "@/lib/api/resources";
import type { User } from "@/lib/api/types";

export const Route = createFileRoute("/users")({ component: UsersPage });

const platformRoles = [
  ROLES.ADMIN,
  ROLES.LEGAL_MANAGER,
  ROLES.CONTRACT_MANAGER,
  ROLES.COMPLIANCE_OFFICER,
  ROLES.VIEWER,
];

function UsersPage() {
  const { user: currentUser } = useAuth();
  const client = useQueryClient();
  const query = useQuery({ queryKey: ["users"], queryFn: users.list });

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 8;

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: ROLES.VIEWER,
    is_active: true,
  });
  const [editing, setEditing] = useState<User | null>(null);
  const [busy, setBusy] = useState(false);

  const filtered = useMemo(() => {
    return (query.data ?? []).filter((item) => {
      const matchesSearch = `${item.full_name} ${item.email}`
        .toLowerCase()
        .includes(search.toLowerCase());
      const matchesRole = !roleFilter || normalizeRole(item.role) === normalizeRole(roleFilter);
      const matchesStatus =
        !statusFilter || (item.is_active ? "Active" : "Inactive") === statusFilter;
      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [query.data, roleFilter, search, statusFilter]);

  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const visible = filtered.slice((page - 1) * pageSize, page * pageSize);

  const resetForm = () => {
    setForm({
      full_name: "",
      email: "",
      password: "",
      role: ROLES.VIEWER,
      is_active: true,
    });
    setEditing(null);
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    try {
      if (editing) {
        await users.update(editing.id, {
          full_name: form.full_name,
          email: form.email,
          role: form.role,
          is_active: form.is_active,
          ...(form.password.trim() ? { password: form.password.trim() } : {}),
        });
        toast.success(`User '${form.full_name}' updated successfully.`);
      } else {
        await users.create({
          full_name: form.full_name,
          email: form.email,
          role: form.role,
          password: form.password,
        });
        toast.success(`User '${form.full_name}' created successfully.`);
      }
      resetForm();
      await client.invalidateQueries({ queryKey: ["users"] });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to save user.");
    } finally {
      setBusy(false);
    }
  };

  const toggleActiveStatus = async (targetUser: User) => {
    const nextStatus = !targetUser.is_active;
    const actionLabel = nextStatus ? "activate" : "deactivate";

    if (currentUser?.id === targetUser.id && !nextStatus) {
      toast.error("You cannot deactivate your own active session account.");
      return;
    }

    try {
      await users.update(targetUser.id, { is_active: nextStatus });
      toast.success(
        `User ${targetUser.full_name} is now ${nextStatus ? "Active" : "Inactive"}.`,
      );
      await client.invalidateQueries({ queryKey: ["users"] });
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : `Failed to ${actionLabel} user.`,
      );
    }
  };

  const remove = async (targetUser: User) => {
    if (currentUser?.id === targetUser.id) {
      toast.error("You cannot delete your own admin account.");
      return;
    }

    if (
      !window.confirm(
        `Delete user '${targetUser.full_name}' (${targetUser.email})? This action cannot be undone.`,
      )
    ) {
      return;
    }

    try {
      await users.delete(targetUser.id);
      toast.success(`User '${targetUser.full_name}' deleted successfully.`);
      if (editing?.id === targetUser.id) {
        resetForm();
      }
      await client.invalidateQueries({ queryKey: ["users"] });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to delete user.");
    }
  };

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-5 py-8 lg:px-8">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex items-start gap-4">
          <span className="grid size-10 place-items-center rounded-md bg-jade/10 text-jade">
            <UsersRound className="size-5" />
          </span>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display text-2xl font-semibold">User Management</h1>
              <Badge variant="outline" className="border-jade/30 text-jade text-xs">
                Admin Console
              </Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Create accounts, assign roles, reset passwords, and manage activation status.
            </p>
          </div>
        </div>
        <label className="flex h-9 items-center gap-2 rounded-md bg-secondary px-3 text-sm">
          <Search className="size-4 text-muted-foreground" />
          <input
            className="w-56 bg-transparent outline-none placeholder:text-muted-foreground"
            placeholder="Search name or email…"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
          />
        </label>
      </header>

      {/* Form Section: Create or Edit */}
      <section className="rounded-lg border border-border/80 bg-card p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold text-foreground">
            {editing ? `Edit User: ${editing.full_name}` : "Create New User"}
          </h2>
          {editing && (
            <Badge variant="secondary" className="text-xs">
              Editing ID #{editing.id}
            </Badge>
          )}
        </div>

        <form className="grid gap-4 md:grid-cols-4" onSubmit={submit}>
          <Field
            label="Full Name"
            value={form.full_name}
            onChange={(value) => setForm({ ...form, full_name: value })}
            placeholder="e.g. Jane Doe"
          />
          <Field
            label="Email Address"
            type="email"
            value={form.email}
            onChange={(value) => setForm({ ...form, email: value })}
            placeholder="e.g. jane@contractiq.com"
          />
          <Field
            label={editing ? "Reset Password (Optional)" : "Password"}
            type="password"
            required={!editing}
            value={form.password}
            onChange={(value) => setForm({ ...form, password: value })}
            placeholder={editing ? "Leave blank to keep existing" : "Min 8 characters"}
          />
          <Select
            label="Assign Role"
            value={form.role}
            options={platformRoles}
            onChange={(value) => setForm({ ...form, role: value })}
          />

          {editing && (
            <div className="flex items-center gap-2 md:col-span-4">
              <label className="flex items-center gap-2 text-sm font-medium text-foreground cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  className="size-4 rounded border-border text-jade focus:ring-jade"
                />
                <span>Account is Active</span>
              </label>
            </div>
          )}

          <div className="flex gap-2 md:col-span-4 pt-2">
            <Button
              type="submit"
              disabled={busy}
              className="bg-jade text-primary-foreground hover:bg-jade/90"
            >
              {busy ? "Saving…" : editing ? "Save Changes" : "Create User"}
            </Button>
            {editing ? (
              <Button type="button" variant="ghost" onClick={resetForm}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
      </section>

      {/* Users Table Section */}
      <section className="rounded-lg border border-border/80 bg-card shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border p-4">
          <div className="flex flex-wrap items-center gap-3">
            <SelectFilter
              label="Filter by Role"
              value={roleFilter}
              options={platformRoles}
              onChange={(value) => {
                setRoleFilter(value);
                setPage(1);
              }}
            />
            <SelectFilter
              label="Filter by Status"
              value={statusFilter}
              options={["Active", "Inactive"]}
              onChange={(value) => {
                setStatusFilter(value);
                setPage(1);
              }}
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Showing {visible.length} of {filtered.length} users
          </p>
        </div>

        {query.isLoading ? (
          <div className="space-y-2 p-4">
            {[1, 2, 3, 4].map((item) => (
              <Skeleton key={item} className="h-14 w-full" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead>
                <tr className="border-b border-border text-xs text-muted-foreground bg-muted/30">
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Assigned Role</th>
                  <th className="px-4 py-3">Last Login</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((userItem) => {
                  const isCurrent = currentUser?.id === userItem.id;
                  return (
                    <tr
                      key={userItem.id}
                      className="border-b border-border/60 hover:bg-muted/20 transition-colors last:border-0"
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <Avatar className="size-9 ring-1 ring-border">
                            <AvatarImage src={userItem.avatar_url ?? undefined} />
                            <AvatarFallback className="text-xs font-semibold">
                              {userItem.full_name
                                .split(" ")
                                .map((part) => part[0])
                                .join("")
                                .slice(0, 2)
                                .toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-foreground">{userItem.full_name}</p>
                              {isCurrent && (
                                <Badge variant="secondary" className="text-[10px] py-0 px-1.5">
                                  You
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground">{userItem.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant="outline"
                          className="border-jade/30 bg-jade/5 text-jade font-medium text-xs"
                        >
                          {userItem.role}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">
                        {userItem.last_login
                          ? new Date(userItem.last_login).toLocaleString()
                          : "Never"}
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={userItem.is_active ? "default" : "secondary"}
                          className={
                            userItem.is_active
                              ? "bg-emerald-500/15 text-emerald-600 hover:bg-emerald-500/20 border-emerald-500/30"
                              : "bg-muted text-muted-foreground"
                          }
                        >
                          {userItem.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Toggle Active Status */}
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-8 text-xs gap-1"
                            title={userItem.is_active ? "Deactivate user" : "Activate user"}
                            onClick={() => toggleActiveStatus(userItem)}
                            disabled={isCurrent && userItem.is_active}
                          >
                            {userItem.is_active ? (
                              <>
                                <UserX className="size-3.5 text-amber-600" />
                                <span className="hidden lg:inline text-amber-600">Deactivate</span>
                              </>
                            ) : (
                              <>
                                <UserCheck className="size-3.5 text-emerald-600" />
                                <span className="hidden lg:inline text-emerald-600">Activate</span>
                              </>
                            )}
                          </Button>

                          {/* Edit User */}
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-8 text-xs"
                            onClick={() => {
                              setEditing(userItem);
                              setForm({
                                full_name: userItem.full_name,
                                email: userItem.email,
                                password: "",
                                role: normalizeRole(userItem.role) || ROLES.VIEWER,
                                is_active: userItem.is_active,
                              });
                              window.scrollTo({ top: 0, behavior: "smooth" });
                            }}
                          >
                            Edit
                          </Button>

                          {/* Delete User */}
                          <Button
                            size="icon"
                            variant="ghost"
                            className="size-8 text-muted-foreground hover:text-destructive"
                            title={isCurrent ? "Cannot delete own account" : "Delete user"}
                            disabled={isCurrent}
                            onClick={() => remove(userItem)}
                          >
                            <Trash2 className="size-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {!query.isLoading && !visible.length ? (
          <p className="p-10 text-center text-sm text-muted-foreground">
            No users match the current filters.
          </p>
        ) : null}

        <div className="flex items-center justify-between border-t border-border p-4 text-sm">
          <span className="text-muted-foreground">
            Page {page} of {pages}
          </span>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={page <= 1}
              onClick={() => setPage((value) => value - 1)}
            >
              Previous
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={page >= pages}
              onClick={() => setPage((value) => value + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </section>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required = true,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <label className="space-y-1.5 text-sm">
      <Label>{label}</Label>
      <Input
        type={type}
        required={required}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="space-y-1.5 text-sm">
      <Label>{label}</Label>
      <select
        className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-jade"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function SelectFilter({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-xs text-muted-foreground">
      <span>{label}:</span>
      <select
        className="h-8 rounded-md border border-input bg-background px-2.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-jade"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">All</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
