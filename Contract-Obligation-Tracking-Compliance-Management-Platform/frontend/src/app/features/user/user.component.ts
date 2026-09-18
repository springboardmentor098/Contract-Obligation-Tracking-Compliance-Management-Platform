import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { UserService } from '../../core/services/user.service';
import { RoleService } from '../../core/services/role.service';

import {
  UserRole,
  ALL_ROLES
} from '../../core/models/roles';

import {
  User
} from '../../core/models/models';

@Component({
  selector: 'cq-users',
  standalone: true,

  imports: [
    CommonModule,
    FormsModule
  ],

  templateUrl: './user.component.html',
  styleUrl: './user.component.css'
})
export class UserComponent {

  private readonly userService =
    inject(UserService);

  private readonly roleService =
    inject(RoleService);


  // ============================================================
  // DATA
  // ============================================================

  users: User[] = [];

  filteredUsers: User[] = [];


  // ============================================================
  // UI STATE
  // ============================================================

  loading = false;

  saving = false;

  error = '';

  success = '';

  searchTerm = '';

  selectedRole = '';


  // ============================================================
  // FORM
  // ============================================================

  showForm = false;

  editingUser: User | null = null;


  form = {

    full_name: '',

    email: '',

    password: '',

    role: UserRole.Employee,

    is_active: true

  };


  // ============================================================
  // ROLES
  // ============================================================

  roles = ALL_ROLES;


  // ============================================================
  // RBAC
  // ============================================================

  get canManageUsers(): boolean {

    return this.roleService.hasPermission(
      'Manage Users'
    );

  }


  get isAdmin(): boolean {

    return this.roleService.isAdmin();

  }


  // ============================================================
  // CONSTRUCTOR
  // ============================================================

  constructor() {

    this.loadUsers();

  }


  // ============================================================
  // LOAD
  // ============================================================

  loadUsers(): void {

    if (!this.canManageUsers) {

      this.error =
        'You do not have permission to manage users.';

      return;

    }


    this.loading = true;

    this.error = '';

    this.success = '';


    this.userService
      .list()
      .subscribe({

        next: (users) => {

          this.users = users ?? [];

          this.applyFilters();

          this.loading = false;

        },

        error: (error) => {

          console.error(
            'Failed to load users:',
            error
          );

          this.error =
            error?.error?.detail ||
            'Unable to load users.';

          this.loading = false;

        }

      });

  }


  // ============================================================
  // FILTER
  // ============================================================

  applyFilters(): void {

    const search =
      this.searchTerm
        .trim()
        .toLowerCase();


    this.filteredUsers =
      this.users.filter(user => {

        const matchesSearch =
          !search ||

          String(user.id)
            .includes(search) ||

          (user.full_name ?? '')
            .toLowerCase()
            .includes(search) ||

          (user.email ?? '')
            .toLowerCase()
            .includes(search);


        const matchesRole =
          !this.selectedRole ||
          user.role === this.selectedRole;


        return (
          matchesSearch &&
          matchesRole
        );

      });

  }


  // ============================================================
  // CREATE
  // ============================================================

  openCreate(): void {

    this.editingUser = null;

    this.error = '';

    this.success = '';


    this.form = {

      full_name: '',

      email: '',

      password: '',

      role: UserRole.Employee,

      is_active: true

    };


    this.showForm = true;

  }


  // ============================================================
  // EDIT
  // ============================================================

  openEdit(user: User): void {

    this.editingUser = user;

    this.error = '';

    this.success = '';


    this.form = {

      full_name:
        user.full_name ?? '',

      email:
        user.email ?? '',

      password: '',

      role:
        user.role as UserRole,

      is_active:
        user.is_active

    };


    this.showForm = true;

  }


  // ============================================================
  // CLOSE
  // ============================================================

  closeForm(): void {

    this.showForm = false;

    this.editingUser = null;

  }


  // ============================================================
  // SAVE
  // ============================================================

  saveUser(): void {

    this.error = '';

    this.success = '';


    const email =
      this.form.email.trim();


    if (!email) {

      this.error =
        'Email is required.';

      return;

    }


    if (!this.editingUser &&
        !this.form.password.trim()) {

      this.error =
        'Password is required when creating a user.';

      return;

    }


    this.saving = true;


    // ----------------------------------------------------------
    // CREATE
    // ----------------------------------------------------------

    if (!this.editingUser) {

      const payload = {

        email,

        password:
          this.form.password,

        full_name:
          this.form.full_name.trim(),

        role:
          this.form.role

      };


      this.userService
        .create(payload)
        .subscribe({

          next: () => {

            this.saving = false;

            this.closeForm();

            this.success =
              'User created successfully.';

            this.loadUsers();

          },

          error: (error) => {

            console.error(
              'Create user error:',
              error
            );

            this.saving = false;

            this.error =
              error?.error?.detail ||
              'Unable to create user.';

          }

        });

      return;

    }


    // ----------------------------------------------------------
    // UPDATE
    // ----------------------------------------------------------

    const payload: any = {

      email,

      full_name:
        this.form.full_name.trim(),

      role:
        this.form.role,

      is_active:
        this.form.is_active

    };


    if (this.form.password.trim()) {

      payload.password =
        this.form.password;

    }


    this.userService
      .update(
        this.editingUser.id,
        payload
      )
      .subscribe({

        next: () => {

          this.saving = false;

          this.closeForm();

          this.success =
            'User updated successfully.';

          this.loadUsers();

        },

        error: (error) => {

          console.error(
            'Update user error:',
            error
          );

          this.saving = false;

          this.error =
            error?.error?.detail ||
            'Unable to update user.';

        }

      });

  }


  // ============================================================
  // ACTIVATE / DEACTIVATE
  // ============================================================

  toggleStatus(user: User): void {

    const action =
      user.is_active
        ? 'deactivate'
        : 'activate';


    if (
      !window.confirm(
        `Are you sure you want to ${action} ${user.email}?`
      )
    ) {

      return;

    }


    this.userService
      .update(
        user.id,
        {
          is_active:
            !user.is_active
        }
      )
      .subscribe({

        next: () => {

          this.success =
            `User ${action}d successfully.`;

          this.loadUsers();

        },

        error: (error) => {

          console.error(
            'Status update error:',
            error
          );

          this.error =
            error?.error?.detail ||
            'Unable to update user status.';

        }

      });

  }


  // ============================================================
  // DELETE
  // ============================================================

  deleteUser(user: User): void {

    if (
      !window.confirm(
        `Are you sure you want to permanently delete ${user.email}?`
      )
    ) {

      return;

    }


    this.userService
      .delete(user.id)
      .subscribe({

        next: () => {

          this.success =
            'User deleted successfully.';

          this.loadUsers();

        },

        error: (error) => {

          console.error(
            'Delete user error:',
            error
          );

          this.error =
            error?.error?.detail ||
            'Unable to delete user.';

        }

      });

  }

}