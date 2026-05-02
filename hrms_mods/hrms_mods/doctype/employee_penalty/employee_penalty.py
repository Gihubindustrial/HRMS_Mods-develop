# Copyright (c) 2026, takamol and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EmployeePenalty(Document):
	def validate(self):
		self._validate_employee()
		self._validate_penalty_component()
		self._validate_amount()
		self._set_default_status()

	def on_submit(self):
		self._create_or_link_additional_salary()
		self.db_set("status", "Submitted", update_modified=False)

	def on_cancel(self):
		self.db_set("status", "Cancelled", update_modified=False)

	def _validate_employee(self):
		if not self.employee:
			frappe.throw(_("Employee is required."))

		status = frappe.db.get_value("Employee", self.employee, "status")
		if status and status.strip().lower() != "active":
			frappe.throw(_("Employee {0} is not active.").format(self.employee))

		if not self.company:
			self.company = frappe.db.get_value("Employee", self.employee, "company")

	def _validate_penalty_component(self):
		if not self.penalty_type:
			frappe.throw(_("Penalty Type is required."))

		component_type = frappe.db.get_value("Salary Component", self.penalty_type, "type")
		if component_type != "Deduction":
			frappe.throw(
				_("Penalty Type must be a Salary Component of type Deduction.")
			)

	def _validate_amount(self):
		if flt(self.penalty_amount) <= 0:
			frappe.throw(_("Penalty Amount must be greater than 0."))

	def _set_default_status(self):
		if self.docstatus == 0 and not self.status:
			self.status = "Draft"

	def _create_or_link_additional_salary(self):
		if self.additional_salary_link:
			return

		existing = frappe.db.get_value(
			"Additional Salary",
			{
				"ref_doctype": "Employee Penalty",
				"ref_docname": self.name,
				"docstatus": ("<", 2),
			},
			"name",
		)
		if existing:
			self.db_set("additional_salary_link", existing, update_modified=False)
			self.db_set("result", _("Additional Salary draft already linked."), update_modified=False)
			return

		additional_salary = frappe.get_doc(
			{
				"doctype": "Additional Salary",
				"employee": self.employee,
				"company": self.company,
				"salary_component": self.penalty_type,
				"amount": flt(self.penalty_amount),
				"payroll_date": self.payroll_date or self.date,
				"is_recurring": 0,
				"overwrite_salary_structure_amount": 1,
				"ref_doctype": "Employee Penalty",
				"ref_docname": self.name,
			}
		)
		additional_salary.insert(ignore_permissions=True)

		self.db_set("additional_salary_link", additional_salary.name, update_modified=False)
		self.db_set("result", _("Additional Salary draft created."), update_modified=False)
