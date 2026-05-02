# HRMS Mods

`hrms_mods` is a custom Frappe app that extends HRMS/ERPNext HR and payroll flows.

It adds employee-document management, overtime request tracking APIs, service-certificate validation, expense filtering for G&A employees, petty-cash and HR payment doctypes, payroll-entry override logic, and Arabic translations for app-facing strings.

## Compatibility and Dependencies

- Framework: Frappe (bench-managed)
- Functional dependencies:
  - `hrms` (for payroll/shift doctypes and payroll override base classes)
  - `erpnext` (for Employee, Expense Claim, Salary Slip, etc.)

## Installation

Run from your bench root:

```bash
bench get-app /path/to/hrms_mods
bench --site <site-name> install-app hrms_mods
bench --site <site-name> migrate
bench --site <site-name> clear-cache
```

If frontend assets are in use:

```bash
bench build
```

## App Structure Overview

- App module: `hrms_mods/hrms_mods`
- Functional module in Desk: `HRMS Mods`
- Hooks: `hrms_mods/hrms_mods/hooks.py`
- Doctypes: `hrms_mods/hrms_mods/hrms_mods/doctype`
- Report: `hrms_mods/hrms_mods/hrms_mods/report/monthly_salary_comparison`
- Notification: `hrms_mods/hrms_mods/hrms_mods/notification/employee_document_expiry_notification`
- JS customizations: `hrms_mods/hrms_mods/public/js`
- Translations: `hrms_mods/hrms_mods/translations/ar.csv`

## Features

### 1) Employee Document Management

#### Employee Document Type
- Doctype: `Employee Document Type`
- Purpose: master list of document categories
- Fields:
  - `type_name` (unique)
  - `description`
  - `has_expiry_date`

#### Employee Document
- Doctype: `Employee Document`
- Purpose: store employee-linked document records and attachments
- Core fields:
  - `employee`
  - `document_type` (link to `Employee Document Type`)
  - `attachment`
  - `issue_date`, `expiry_date`
  - `is_signed`
  - `notes`

#### Expiry Notification
- Notification: `Employee document Expiry notification`
- Trigger: `Days Before` on `expiry_date` (30 days)
- Recipients: `HR Manager`, `HR User`
- Channel: Email + system notification

#### Employee Form Button
- JS Hook via `hooks.py`:
  - `Employee` uses `public/js/employee_bundle.js`
- Adds a dedicated **Employee Documents** button on Employee form
- Button routes to filtered Employee Document list for selected employee

### 2) Overtime Request and Tracking

#### Overtime Request Doctype
- Doctype: `Overtime Request`
- Submittable with status tracking fields
- Core data:
  - employee/date/time range (`from_time`, `to_time`)
  - optional shift metadata (`shift_type`, `shift_assignment`, shift times)
  - auto-calculated `overtime_hours`
  - status timeline fields (`requested_by`, `approved_by`, `rejected_by`, etc.)

#### Overtime Controller Logic
File: `hrms_mods/hrms_mods/hrms_mods/doctype/overtime_request/overtime_request.py`

- Validates employee is active
- Auto-calculates overtime hours (including overnight spans)
- Attempts to map active shift assignment when available
- Allows creation even if no shift assignment is found
- Prevents duplicates for same employee/date/time/shift bucket
- Maintains timestamp/user audit fields based on status

#### Overtime API (Whitelisted)
File: `hrms_mods/hrms_mods/hrms_mods/api/overtime.py`

Available methods:

- `request_overtime(employee, overtime_date, from_time, to_time, shift_type=None, reason=None)`
- `get_overtime_tracking(employee=None, from_date=None, to_date=None, status=None)`
- `approve_overtime_request(name, manager_remarks=None)`
- `reject_overtime_request(name, manager_remarks=None)`
- `cancel_overtime_request(name, manager_remarks=None)`

Security model:
- HR roles (`HR Manager`, `HR User`, `System Manager`) have broader access
- Employee users are constrained to their own employee record
- Non-eligible roles are blocked

### 3) Service Certificate Validation

Doctype: `Service Certificate`  
Controller: `service_certificate.py`

Rules enforced:
- Employee is required
- Employee status must be `Left`
- Joining/relieving dates are validated
- Prevents duplicate certificates for same employee and period

### 4) Excuse for Attendance Validation

Doctype: `Excuse for Attendance`  
Controller: `excuse_for_attendance.py`

Rules enforced:
- Duplicate prevention for employee/date/from/to range
- Employee must be active
- Auto-fills leave approver from Employee when empty

### 5) Payroll Entry Override (Custom Payroll Logic)

File: `overrides/payroll_entry.py`  
Class: `CustomPayrollEntry(PayrollEntry)`

Includes:
- Customized salary component aggregation
- Employer contribution journal entry generation
- Bank entry behavior with employer-contribution handling
- Loan repayment handling in payroll bank entry flow

> Note: The override class exists in code, while the `override_doctype_class` hook entry is commented in `hooks.py`. Enable hook mapping when you want this override active.

### 6) Monthly Salary Comparison Report

- Report: `Monthly Salary Comparison` (Script Report)
- Reference doctype: `Salary Slip`
- Roles: `HR Manager`, `HR User`
- Supports:
  - detailed monthly employee salary breakdown
  - summarized monthly employee count + total salary
  - company/employee/department/cost-center based filtering

### 7) Expense Claim G&A Filtering

JS file: `public/js/expense_claim_gna_filter.js`  
Bound on `Expense Claim`.

Behavior:
- Reads Employee flag `is_gna_employee`
- Filters child-table `expense_type` options based on Expense Claim Type flag `is_gna_expense`
- Refreshes/clears expenses grid when employee changes

### 8) Full and Final Statement Enhancement

JS file: `public/js/full_and_final_statement.js`  
Custom Field patch/migration adds:
- `custom_total_amount` on `Full and Final Statement`

Client-side calculation:
- `custom_total_amount = total_payable_amount - total_receivable_amount`

### 9) Additional HR Utility Doctypes

- `Nationality List` (master doctype)
- `HR Payment Type` (master doctype)
- `HR Payment Order` (transaction doctype)
- `Petty Cash Request` (submittable doctype)

## Hooks and Registered Integrations

From `hooks.py`:

- `doctype_js`:
  - `Full and Final Statement` -> `public/js/full_and_final_statement.js`
  - `Employee` -> `public/js/employee_bundle.js`
  - `Expense Claim` -> `public/js/expense_claim_gna_filter.js`

- `after_migrate`:
  - `hrms_mods.hrms_mods.utils.seed_employee_document_types.after_migrate`

- Fixtures:
  - `Nationality List`

- Patches list (in hooks):
  - `hrms_mods.hrms_mods.patches.add_nationality_field.add_nationality_field`
  - `hrms_mods.hrms_mods.patches.add_gna_fields.add_gna_fields`

## Patches and Migrations

### Patches (`hrms_mods/hrms_mods/patches`)

1. `add_nationality_field.py`
   - Adds `country` custom field (label: Nationality) to Employee
   - Link target: `Nationality List`

2. `add_gna_fields.py`
   - Adds `is_gna_employee` checkbox to Employee
   - Adds `is_gna_expense` checkbox to Expense Claim Type

### Migrations (`hrms_mods/hrms_mods/migrations`)

1. `20231024_create_custom_field.py`
   - Adds `custom_total_amount` field to Full and Final Statement

2. `20260325_seed_employee_document_types.py`
   - Delegates to seeded defaults helper
   - Ensures default Employee Document Types exist

### Post-Migrate Seeder

File: `hrms_mods/hrms_mods/hrms_mods/utils/seed_employee_document_types.py`

Ensures default document types such as:
- Passport
- Iqama (Residence Permit)
- Saudi Visa
- Work Permit
- Medical Insurance
- Saudi National ID
- Educational Certificate
- Experience Certificate
- CV / Resume
- No Objection Certificate (NOC)

## Translations

- Arabic translations are provided in:
  - `hrms_mods/hrms_mods/translations/ar.csv`

This includes translations for overtime messages, report labels, and UI messages added by app JS.

## Development Notes

- The app contains legacy/commented JS files (`employee.js`, `employee_documents_button.js`) kept in repository but not wired in hooks.
- For any structural change (doctype fields/workflows/permissions), run:

```bash
bench --site <site-name> migrate
```

## License

MIT