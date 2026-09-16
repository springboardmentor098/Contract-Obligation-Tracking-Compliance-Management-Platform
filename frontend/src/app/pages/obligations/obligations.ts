import {
  Component,
  OnInit,
  ChangeDetectorRef,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  Obligation,
  ObligationCreate,
  ObligationService
} from '../../core/services/obligation.service';

@Component({
  selector: 'app-obligations',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './obligations.html',
  styleUrl: './obligations.scss'
})
export class Obligations implements OnInit {

  private readonly obligationService =
    inject(ObligationService);

  private readonly fb = inject(FormBuilder);

  private readonly cdr =
    inject(ChangeDetectorRef);

  obligations: Obligation[] = [];

  loading = true;
  saving = false;

  showForm = false;

  error = '';

  obligationForm = this.fb.nonNullable.group({
    contract_id: [0, [Validators.required, Validators.min(1)]],
    title: ['', [Validators.required]],
    description: [''],
    due_date: ['', [Validators.required]],
    priority: ['medium', [Validators.required]],
    responsible_party: ['']
  });

  ngOnInit(): void {
    this.loadObligations();
  }

  loadObligations(): void {

    this.loading = true;
    this.error = '';

    this.obligationService
      .getObligations()
      .subscribe({

        next: (data) => {

          console.log(
            'Obligations loaded:',
            data
          );

          this.obligations = data;
          this.loading = false;

          this.cdr.detectChanges();
        },

        error: (err) => {

          console.error(
            'Obligations API error:',
            err
          );

          this.loading = false;

          this.error =
            'Unable to load obligations.';

          this.cdr.detectChanges();
        }

      });
  }

  openCreateForm(): void {

    this.obligationForm.reset({
      contract_id: 0,
      title: '',
      description: '',
      due_date: '',
      priority: 'medium',
      responsible_party: ''
    });

    this.error = '';
    this.showForm = true;
  }

  cancelCreate(): void {

    this.showForm = false;
    this.error = '';
  }

  createObligation(): void {

    if (this.obligationForm.invalid) {

      this.obligationForm.markAllAsTouched();

      return;
    }

    this.saving = true;
    this.error = '';

    const value =
      this.obligationForm.getRawValue();

    const payload: ObligationCreate = {

      contract_id: Number(
        value.contract_id
      ),

      title: value.title.trim(),

      description:
        value.description.trim() || null,

      due_date: value.due_date,

      priority: value.priority,

      responsible_party:
        value.responsible_party.trim() || null
    };

    this.obligationService
      .createObligation(payload)
      .subscribe({

        next: (created) => {

          console.log(
            'Obligation created:',
            created
          );

          this.obligations = [
            created,
            ...this.obligations
          ];

          this.showForm = false;
          this.saving = false;

          this.cdr.detectChanges();
        },

        error: (err) => {

          console.error(
            'Create obligation error:',
            err
          );

          this.saving = false;

          this.error =
            err.error?.detail ||
            'Unable to create obligation.';

          this.cdr.detectChanges();
        }

      });
  }

  changeStatus(
    obligation: Obligation,
    newStatus: string
  ): void {

    const confirmed =
      window.confirm(
        `Change "${obligation.title}" from "${obligation.status}" to "${newStatus}"?`
      );

    if (!confirmed) {
      return;
    }

    this.obligationService
      .updateStatus(
        obligation.id,
        newStatus
      )
      .subscribe({

        next: (updated) => {

          console.log(
            'Obligation status updated:',
            updated
          );

          this.obligations =
            this.obligations.map(item =>
              item.id === updated.id
                ? updated
                : item
            );

          this.cdr.detectChanges();
        },

        error: (err) => {

          console.error(
            'Status update error:',
            err
          );

          this.error =
            err.error?.detail ||
            'Unable to update obligation status.';

          this.cdr.detectChanges();
        }

      });
  }

  deleteObligation(
    obligation: Obligation
  ): void {

    const confirmed =
      window.confirm(
        `Delete obligation "${obligation.title}"?`
      );

    if (!confirmed) {
      return;
    }

    this.obligationService
      .deleteObligation(obligation.id)
      .subscribe({

        next: () => {

          this.obligations =
            this.obligations.filter(
              item =>
                item.id !== obligation.id
            );

          this.cdr.detectChanges();
        },

        error: (err) => {

          console.error(
            'Delete obligation error:',
            err
          );

          this.error =
            err.error?.detail ||
            'Unable to delete obligation.';

          this.cdr.detectChanges();
        }

      });
  }

  scanOverdue(): void {

    this.obligationService
      .scanOverdue()
      .subscribe({

        next: (result) => {

          console.log(
            'Overdue scan:',
            result
          );

          this.loadObligations();
        },

        error: (err) => {

          console.error(
            'Overdue scan error:',
            err
          );

          this.error =
            err.error?.detail ||
            'Unable to scan overdue obligations.';
        }

      });
  }
}
