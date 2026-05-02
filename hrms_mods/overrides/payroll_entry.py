from frappe import _
import frappe
from frappe.utils import flt
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
)
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from hrms.payroll.doctype.salary_withholding.salary_withholding import link_bank_entry_in_salary_withholdings
from hrms.payroll.doctype.payroll_entry.payroll_entry import submit_salary_slips_for_employees

class CustomPayrollEntry(PayrollEntry):

    def get_salary_component_total(
        self, component_type=None, include_employer_contribution=False, employee_wise_accounting_enabled=False
    ):
        """
        Get the total for salary components.
        Includes logic for handling custom employer contributions.
        """
        salary_components = self.get_salary_components(component_type)
        component_dict = {}

        for item in salary_components:
            if not self.should_add_component_to_accrual_jv(component_type, item):
                continue

            # Handle custom employer contributions
            is_employer_contribution = frappe.db.get_value(
                "Salary Component",
                item.salary_component,
                "custom_employer_contribution"
            )
            if component_type == "deductions" and not include_employer_contribution and is_employer_contribution:
                continue

            cost_centers = self.get_payroll_cost_centers_for_employee(item.employee, item.salary_structure)
            for cost_center, percentage in cost_centers.items():
                amount = flt(item.amount) * percentage / 100
                key = (item.salary_component, cost_center)
                component_dict[key] = component_dict.get(key, 0) + amount

        return self.get_account(component_dict=component_dict)

    @frappe.whitelist()
    def submit_salary_slips(self):
        """
        Submit salary slips and create journal entries for employer contributions.
        """
        self.check_permission("write")

        # Get the list of salary slips to process
        salary_slips = self.get_sal_slip_list(ss_status=0)

        if len(salary_slips) > 30 or frappe.flags.enqueue_payroll_entry:
            # Queue the submission process for larger batches
            self.db_set("status", "Queued")
            frappe.enqueue(
                submit_salary_slips_for_employees,
                timeout=3000,
                payroll_entry=self,
                salary_slips=salary_slips,
                publish_progress=False,
            )
            frappe.msgprint(
                _("Salary Slip submission is queued. It may take a few minutes"),
                alert=True,
                indicator="blue",
            )
        else:
            # Call the function directly for smaller batches
            submit_salary_slips_for_employees(self, salary_slips, publish_progress=False)

        # Add custom logic for employer contribution journal entries
        self.create_employer_contribution_journal_entry(submitted_salary_slips=salary_slips)

    def create_employer_contribution_journal_entry(self, submitted_salary_slips):
        """
        Create a journal entry for employer contributions.
        """
        contributions = self.get_salary_component_total(
            component_type="deductions", include_employer_contribution=True
        )

        if not contributions:
            return

        accounts = []
        currencies = []
        company_currency = frappe.get_cached_value("Company", self.company, "default_currency")
        accounting_dimensions = frappe.get_cached_value("Company", self.company, "accounting_dimensions") or []
        precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

        for (salary_component, cost_center), amount in contributions.items():
            employer_account = frappe.db.get_value(
                "Salary Component", salary_component, "custom_employer_contribution"
            )
            payable_account = frappe.db.get_value(
                "Salary Component", salary_component, "custom_payable_account"
            )

            if not employer_account or not payable_account:
                frappe.throw(
                    _("Employer Contribution or Payable Account is not set for Salary Component {0}").format(
                        frappe.bold(salary_component)
                    )
                )

            # Debit Employer Contribution Account
            accounts.append({
                "account": employer_account,
                "debit_in_account_currency": flt(amount, precision),
                "cost_center": cost_center,
                "exchange_rate": 1,
            })

            # Credit Payable Account
            accounts.append({
                "account": payable_account,
                "credit_in_account_currency": flt(amount, precision),
                "cost_center": cost_center,
                "exchange_rate": 1,
            })

        # Create the journal entry
        self.make_journal_entry(
            accounts=accounts,
            currencies=currencies,
            voucher_type="Journal Entry",
            user_remark=_("Employer Contribution for payroll from {0} to {1}").format(
                self.start_date, self.end_date
            ),
            submit_journal_entry=True,
            submitted_salary_slips=submitted_salary_slips,
        )


    @frappe.whitelist()
    def make_bank_entry(self, for_withheld_salaries=False):
        self.check_permission("write")
        self.employee_based_payroll_payable_entries = {}
        employee_wise_accounting_enabled = frappe.db.get_single_value(
            "Payroll Settings", "process_payroll_accounting_entry_based_on_employee"
        )

        salary_slip_total = 0
        salary_details = self.get_salary_slip_details(for_withheld_salaries)

        for salary_detail in salary_details:
            if salary_detail.parentfield == "earnings":
                (
                    is_flexible_benefit,
                    only_tax_impact,
                    create_separate_je,
                    statistical_component,
                ) = frappe.db.get_value(
                    "Salary Component",
                    salary_detail.salary_component,
                    (
                        "is_flexible_benefit",
                        "only_tax_impact",
                        "create_separate_payment_entry_against_benefit_claim",
                        "statistical_component",
                    ),
                    cache=True,
                )

                if only_tax_impact != 1 and statistical_component != 1:
                    if is_flexible_benefit == 1 and create_separate_je == 1:
                        self.set_accounting_entries_for_bank_entry(
                            salary_detail.amount, salary_detail.salary_component
                        )
                    else:
                        if employee_wise_accounting_enabled:
                            self.set_employee_based_payroll_payable_entries(
                                "earnings",
                                salary_detail.employee,
                                salary_detail.amount,
                                salary_detail.salary_structure,
                            )
                        salary_slip_total += salary_detail.amount

            if salary_detail.parentfield == "deductions":
                (
                    is_employer_contribution,
                    statistical_component,
                ) = frappe.db.get_value(
                    "Salary Component",
                    salary_detail.salary_component,
                    ["custom_employer_contribution", "statistical_component"],
                    as_dict=True,
                )

                if is_employer_contribution or statistical_component:
                    continue

                if employee_wise_accounting_enabled:
                    self.set_employee_based_payroll_payable_entries(
                        "deductions",
                        salary_detail.employee,
                        salary_detail.amount,
                        salary_detail.salary_structure,
                    )

                salary_slip_total -= salary_detail.amount

        # Add loan repayments
        total_loan_repayment = self.process_loan_repayments_for_bank_entry(salary_details) or 0
        salary_slip_total -= total_loan_repayment

        bank_entry = None
        if salary_slip_total > 0:
            remark = "withheld salaries" if for_withheld_salaries else "salaries"
            bank_entry = self.set_accounting_entries_for_bank_entry(salary_slip_total, remark)

            if for_withheld_salaries:
                link_bank_entry_in_salary_withholdings(salary_details, bank_entry.name)

        return bank_entry

    def process_loan_repayments_for_bank_entry(self, salary_details):
        """
        Processes loan repayments in salary details and returns the total loan repayment amount.
        """
        unique_salary_slips = {row["employee"]: row for row in salary_details}.values()
        total_loan_repayment = sum(flt(slip.get("total_loan_repayment", 0)) for slip in unique_salary_slips)

        if self.employee_based_payroll_payable_entries:
            for salary_slip in unique_salary_slips:
                if salary_slip.get("total_loan_repayment"):
                    self.set_employee_based_payroll_payable_entries(
                        "total_loan_repayment",
                        salary_slip.employee,
                        salary_slip.total_loan_repayment,
                        salary_slip.salary_structure,
                    )

        return total_loan_repayment