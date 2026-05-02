# Copyright (c) 2026, takamol and contributors
# For license information, please see license.txt

from __future__ import annotations

from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


def _as_minutes(t) -> int:
	"""
	Convert frappe Time field value to minutes.

	Time fields can come as `datetime.time` (server) or `str` (API).
	"""
	if not t:
		return 0

	# `frappe.utils.get_time` is not always imported/available in all contexts.
	if isinstance(t, datetime):
		t = t.time()

	if hasattr(t, "hour"):
		return int(t.hour * 60 + t.minute + (t.second / 60))

	# Expect `HH:MM[:SS]`
	parts = str(t).split(":")
	h = int(parts[0])
	m = int(parts[1]) if len(parts) > 1 else 0
	s = int(parts[2]) if len(parts) > 2 else 0
	return int(h * 60 + m + (s / 60))


def _calculate_overtime_hours(from_time, to_time) -> float:
	start_minutes = _as_minutes(from_time)
	end_minutes = _as_minutes(to_time)

	# Don't treat `00:00` as invalid; only treat missing values as invalid.
	if not from_time or not to_time:
		return 0.0

	duration_minutes = end_minutes - start_minutes
	# If `to_time` is earlier than/equal to `from_time`, treat it as next day.
	if duration_minutes <= 0:
		duration_minutes += 24 * 60

	return flt(duration_minutes / 60.0, 2)


class OvertimeRequest(Document):
	def validate(self):
		self._validate_basics()
		self._validate_employee()
		self._resolve_shift_assignment()
		self._compute_hours()
		self._check_duplicate()
		self._set_action_fields_from_status()

	def _validate_basics(self):
		if not self.employee:
			frappe.throw(_("Employee is required."))
		if not self.overtime_date:
			frappe.throw(_("Overtime Date is required."))
		if not self.from_time or not self.to_time:
			frappe.throw(_("From Time and To Time are required."))

	def _validate_employee(self):
		status = frappe.db.get_value("Employee", self.employee, "status")
		if not status or str(status).strip().lower() != "active":
			frappe.throw(_("Employee {0} is not Active.").format(self.employee))

	def _resolve_shift_assignment(self):
		# Ensure the overtime request is linked to an actual shift assignment in HRMS.
		if not self.employee or not self.overtime_date:
			return

		# If shift_assignment is already set, just align shift_type/company.
		if self.shift_assignment:
			if not self.shift_type:
				self.shift_type = frappe.db.get_value(
					"Shift Assignment", self.shift_assignment, "shift_type"
				)
			if not self.company:
				self.company = frappe.db.get_value("Shift Assignment", self.shift_assignment, "company")
			return

		conditions = [
			"employee = %(employee)s",
			"status = 'Active'",
			"start_date <= %(overtime_date)s",
			"(end_date IS NULL OR end_date >= %(overtime_date)s)",
		]
		params = {"employee": self.employee, "overtime_date": self.overtime_date}

		# If user specified shift_type, constrain to it.
		if self.shift_type:
			conditions.append("shift_type = %(shift_type)s")
			params["shift_type"] = self.shift_type

		rows = frappe.db.sql(
			f"""
			SELECT name, shift_type, company
			FROM `tabShift Assignment`
			WHERE {" AND ".join(conditions)}
			ORDER BY start_date DESC, modified DESC
			LIMIT 2
			""",
			params,
			as_dict=True,
		)

		if not rows:
			# Allow overtime request creation even if no shift assignment is found.
			# Shift metadata fields will remain empty.
			return

		if len(rows) > 1:
			# Avoid silently picking one if data is ambiguous.
			frappe.throw(
				_(
					"Multiple active Shift Assignments found for the selected Employee/Date. Please refine the shift selection."
				)
			)

		self.shift_assignment = rows[0]["name"]
		if not self.shift_type:
			self.shift_type = rows[0]["shift_type"]
		if self.shift_type and self.shift_type != rows[0].get("shift_type"):
			frappe.throw(
				_("Selected Shift Type does not match the employee's active Shift Assignment.")
			)

		# Fill company from the linked HRMS shift assignment (if the field isn't already set).
		if not self.company:
			self.company = rows[0].get("company") or frappe.db.get_value(
				"Shift Assignment", self.shift_assignment, "company"
			)

	def _compute_hours(self):
		self.overtime_hours = _calculate_overtime_hours(self.from_time, self.to_time)
		if self.overtime_hours <= 0:
			frappe.throw(_("Overtime hours must be greater than 0."))

	def _check_duplicate(self):
		# Keep duplicates from cluttering approvals: same employee/date/shift and exact time range.
		shift_condition = "shift_type = %(shift_type)s"
		shift_params = {"shift_type": self.shift_type}
		if not self.shift_type:
			shift_condition = "shift_type IS NULL"
			shift_params = {}

		rows = frappe.db.sql(
			"""
			SELECT name
			FROM `tabOvertime Request`
			WHERE employee = %(employee)s
				AND overtime_date = %(overtime_date)s
				AND """
			+ shift_condition
			+ """
				AND from_time = %(from_time)s
				AND to_time = %(to_time)s
				AND status NOT IN ('Rejected', 'Cancelled')
				AND name != %(name)s
			LIMIT 1
			""",
			{
				"employee": self.employee,
				"overtime_date": self.overtime_date,
				"from_time": self.from_time,
				"to_time": self.to_time,
				"name": self.name or "__new__",
				**shift_params,
			},
			as_dict=True,
		)
		if rows:
			frappe.throw(_("An overtime request with the same details already exists."))

	def _set_action_fields_from_status(self):
		"""
		Set timestamps/by-fields based on current `status`.

		This allows both the API and UI to keep consistent history.
		"""
		user = frappe.session.user
		now = now_datetime()

		if self.status == "Requested":
			if not self.requested_on:
				self.requested_on = now
			if not self.requested_by:
				self.requested_by = user
			# Clear other action fields to keep state unambiguous.
			if self.approved_on and self.approved_by:
				self.approved_on = None
				self.approved_by = None
			if self.rejected_on and self.rejected_by:
				self.rejected_on = None
				self.rejected_by = None
		elif self.status == "Approved":
			if not self.approved_on:
				self.approved_on = now
			if not self.approved_by:
				self.approved_by = user
		elif self.status == "Rejected":
			if not self.rejected_on:
				self.rejected_on = now
			if not self.rejected_by:
				self.rejected_by = user
		elif self.status == "Cancelled":
			if not self.cancelled_on:
				self.cancelled_on = now
			if not self.cancelled_by:
				self.cancelled_by = user

