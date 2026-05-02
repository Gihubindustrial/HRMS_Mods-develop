# Copyright (c) 2026, takamol and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, now_datetime


def _get_current_employee() -> str | None:
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")


def _get_user_roles() -> set[str]:
	return set(frappe.get_roles(frappe.session.user) or [])


def _is_hr_user(roles: set[str] | None = None) -> bool:
	roles = roles or _get_user_roles()
	return "HR Manager" in roles or "HR User" in roles or "System Manager" in roles


def _assert_can_view_employee(employee: str | None):
	"""
	Enforce least-privilege access to overtime requests by employee.

	- HR Manager/HR User/System Manager: can view any employee
	- Employee role: can view only their own records
	- others: blocked
	"""
	user_roles = _get_user_roles()
	if _is_hr_user(user_roles):
		return

	if "Employee" not in user_roles:
		frappe.throw(_("Not permitted."))

	current_employee = _get_current_employee()
	if not current_employee:
		frappe.throw(_("No Employee record is linked to your user."))

	if employee and employee != current_employee:
		frappe.throw(_("You can only view overtime requests for your own record."))


def _assert_is_hr_user():
	if not _is_hr_user():
		frappe.throw(_("Only HR users can approve/reject/cancel overtime requests."))


@frappe.whitelist()
def request_overtime(
	employee: str,
	overtime_date: str,
	from_time: str,
	to_time: str,
	shift_type: str | None = None,
	reason: str | None = None,
):
	"""
	Create an `Overtime Request` record for an employee.

	This function does not change other apps; it only writes within `hrms_mods`.
	"""
	roles = _get_user_roles()
	# Employees can only request for themselves; HR can request for any employee.
	if not _is_hr_user(roles):
		if "Employee" not in roles:
			frappe.throw(_("Not permitted."))
		current_employee = _get_current_employee()
		if not current_employee:
			frappe.throw(_("No Employee record is linked to your user."))
		if employee != current_employee:
			frappe.throw(_("You can only request overtime for your own record."))

	doc = frappe.new_doc("Overtime Request")
	doc.employee = employee
	if shift_type:
		doc.shift_type = shift_type
	doc.overtime_date = overtime_date
	doc.from_time = from_time
	doc.to_time = to_time
	doc.reason = reason
	doc.status = "Requested"

	doc.insert()
	return {"name": doc.name, "status": doc.status, "overtime_hours": doc.overtime_hours}


@frappe.whitelist()
def get_overtime_tracking(
	employee: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	status: str | None = None,
):
	"""
	Get overtime requests for tracking (status + hours).

	- If called by an `Employee` role, `employee` will be restricted to their own record.
	- HR users / HR managers can query any employee.
	"""
	user_roles = _get_user_roles()
	if _is_hr_user(user_roles):
		# HR can query any employee (optional filter).
		pass
	else:
		# Non-HR can only query their own employee record.
		_assert_can_view_employee(employee)
		if not employee:
			employee = _get_current_employee()
			if not employee:
				frappe.throw(_("No Employee record is linked to your user."))

	filters = []
	if employee:
		filters.append(["employee", "=", employee])
	if from_date:
		filters.append(["overtime_date", ">=", from_date])
	if to_date:
		filters.append(["overtime_date", "<=", to_date])
	if status:
		filters.append(["status", "=", status])

	# If no filters were provided and the user isn't an Employee, return recent data only.
	limit = 50
	rows = frappe.get_all(
		"Overtime Request",
		filters=filters or None,
		fields=[
			"name",
			"employee",
			"overtime_date",
			"shift_type",
			"shift_assignment",
			"from_time",
			"to_time",
			"overtime_hours",
			"status",
			"requested_by",
			"requested_on",
			"approved_by",
			"approved_on",
			"rejected_by",
			"rejected_on",
			"cancelled_by",
			"cancelled_on",
			"manager_remarks",
		],
		order_by="overtime_date desc, creation desc",
		limit=limit,
	)

	total_hours = flt(sum([r.get("overtime_hours") or 0 for r in rows]), 2)
	summary = {}
	for r in rows:
		summary.setdefault(r.get("status"), 0)
		summary[r.get("status")] += 1

	return {"total_hours": total_hours, "summary": summary, "requests": rows}


def _get_and_check(name: str):
	doc = frappe.get_doc("Overtime Request", name)
	doc.check_permission("write")
	return doc


@frappe.whitelist()
def approve_overtime_request(name: str, manager_remarks: str | None = None):
	"""
	Approve an existing overtime request (status tracking).
	"""
	_assert_is_hr_user()
	doc = _get_and_check(name)
	if doc.status != "Requested":
		frappe.throw(_("Only Requested overtime requests can be approved."))

	doc.status = "Approved"
	if manager_remarks:
		doc.manager_remarks = manager_remarks

	doc.save()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def reject_overtime_request(name: str, manager_remarks: str | None = None):
	"""
	Reject an existing overtime request (status tracking).
	"""
	_assert_is_hr_user()
	doc = _get_and_check(name)
	if doc.status != "Requested":
		frappe.throw(_("Only Requested overtime requests can be rejected."))

	doc.status = "Rejected"
	if manager_remarks:
		doc.manager_remarks = manager_remarks

	doc.save()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def cancel_overtime_request(name: str, manager_remarks: str | None = None):
	"""
	Cancel an existing overtime request (status tracking).
	"""
	_assert_is_hr_user()
	doc = _get_and_check(name)
	if doc.status in ("Approved",):
		frappe.throw(_("Approved overtime requests cannot be cancelled."))
	if doc.status in ("Cancelled",):
		return {"name": doc.name, "status": doc.status}

	doc.status = "Cancelled"
	if manager_remarks:
		doc.manager_remarks = manager_remarks

	doc.save()
	return {"name": doc.name, "status": doc.status}

