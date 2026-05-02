import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.utils import formatdate


def validate_alternative_employee(doc, _method=None):
    if doc.doctype != "Leave Application":
        return

    if not (doc.employee and doc.from_date and doc.to_date):
        return

    requester_company = frappe.db.get_value("Employee", doc.employee, "company")
    rows = doc.get("alternative_assignments") or []
    rows = [row for row in rows if row.alternative_employee or row.from_date or row.to_date]

    if not rows:
        doc.alternative_assignment_emails = ""
        return

    _auto_fill_single_row_dates_from_parent(doc, rows)
    _validate_intra_document_overlap(rows)

    employee_cache = {}
    recipient_emails = []
    for index, row in enumerate(rows, start=1):
        _validate_row_mandatory_fields(row, index)
        _validate_row_date_bounds(doc, row, index)

        if row.alternative_employee == doc.employee:
            frappe.throw(_("Row #{0}: Alternative Employee cannot be the same as the requester.").format(index))

        alternative = employee_cache.get(row.alternative_employee)
        if not alternative:
            alternative = frappe.db.get_value(
                "Employee",
                row.alternative_employee,
                ["name", "employee_name", "status", "company", "prefered_email", "user_id"],
                as_dict=True,
            )
            employee_cache[row.alternative_employee] = alternative

        if not alternative:
            frappe.throw(
                _("Row #{0}: Alternative Employee {1} does not exist.").format(
                    index, frappe.bold(row.alternative_employee)
                )
            )

        if alternative.status != "Active":
            frappe.throw(
                _("Row #{0}: Alternative Employee {1} is not active.").format(
                    index, frappe.bold(row.alternative_employee)
                )
            )

        if requester_company and alternative.company != requester_company:
            frappe.throw(
                _("Row #{0}: Alternative Employee must belong to the same company as the requester ({1}).").format(
                    index, frappe.bold(requester_company)
                )
            )

        if alternative.prefered_email:
            recipient_emails.append(alternative.prefered_email)
        elif alternative.user_id:
            recipient_emails.append(alternative.user_id)

        _validate_alternative_not_on_leave(doc, row, index)
        _validate_alternative_not_double_assigned(doc, row, index)

    doc.alternative_assignment_emails = ",".join(sorted(set(recipient_emails)))


def _validate_row_mandatory_fields(row, index):
    if not row.alternative_employee:
        frappe.throw(_("Row #{0}: Alternative Employee is required.").format(index))
    if not row.from_date:
        frappe.throw(_("Row #{0}: From Date is required.").format(index))
    if not row.to_date:
        frappe.throw(_("Row #{0}: To Date is required.").format(index))


def _auto_fill_single_row_dates_from_parent(doc, rows):
    # Server-side fallback: if only one coverage row exists and either date is empty,
    # copy from leave application dates before row validations.
    if len(rows) != 1:
        return

    row = rows[0]
    if not row.from_date and doc.from_date:
        row.from_date = doc.from_date
    if not row.to_date and doc.to_date:
        row.to_date = doc.to_date


def _validate_row_date_bounds(doc, row, index):
    if row.from_date > row.to_date:
        frappe.throw(_("Row #{0}: From Date cannot be after To Date.").format(index))

    if row.from_date < doc.from_date or row.to_date > doc.to_date:
        frappe.throw(
            _("Row #{0}: Assignment dates must be within leave period ({1} to {2}).").format(
                index, formatdate(doc.from_date), formatdate(doc.to_date)
            )
        )


def _validate_alternative_not_on_leave(doc, row, index):
    conflict = frappe.db.sql(
        """
        select name, leave_type, from_date, to_date
        from `tabLeave Application`
        where employee = %(employee)s
            and docstatus < 2
            and status in ('Open', 'Approved')
            and to_date >= %(from_date)s
            and from_date <= %(to_date)s
            and name != %(name)s
        order by from_date asc
        limit 1
        """,
        {
            "employee": row.alternative_employee,
            "from_date": row.from_date,
            "to_date": row.to_date,
            "name": doc.name or "New Leave Application",
        },
        as_dict=True,
    )

    if not conflict:
        return

    conflict = conflict[0]
    conflict_link = get_link_to_form("Leave Application", conflict.name)
    frappe.throw(
        _("Row #{0}: Alternative Employee {1} is already on leave ({2}) between {3} and {4} in leave request {5}.").format(
            index,
            frappe.bold(row.alternative_employee),
            frappe.bold(conflict.leave_type),
            formatdate(conflict.from_date),
            formatdate(conflict.to_date),
            conflict_link,
        )
    )


def _validate_alternative_not_double_assigned(doc, row, index):
    conflict = frappe.db.sql(
        """
        select la.name, la.employee, aa.from_date, aa.to_date
        from `tabLeave Application` la
        inner join `tabLeave Alternative Assignment` aa
            on aa.parent = la.name
            and aa.parenttype = 'Leave Application'
            and aa.parentfield = 'alternative_assignments'
        where aa.alternative_employee = %(employee)s
            and la.docstatus < 2
            and la.status in ('Open', 'Approved')
            and aa.to_date >= %(from_date)s
            and aa.from_date <= %(to_date)s
            and la.name != %(name)s
        order by aa.from_date asc
        limit 1
        """,
        {
            "employee": row.alternative_employee,
            "from_date": row.from_date,
            "to_date": row.to_date,
            "name": doc.name or "New Leave Application",
        },
        as_dict=True,
    )

    if not conflict:
        return

    conflict = conflict[0]
    conflict_link = get_link_to_form("Leave Application", conflict.name)
    frappe.throw(
        _("Row #{0}: Alternative Employee {1} is already assigned as alternative for employee {2} between {3} and {4} in leave request {5}.").format(
            index,
            frappe.bold(row.alternative_employee),
            frappe.bold(conflict.employee),
            formatdate(conflict.from_date),
            formatdate(conflict.to_date),
            conflict_link,
        )
    )


def _validate_intra_document_overlap(rows):
    for i in range(len(rows)):
        left = rows[i]
        if not left.alternative_employee or not left.from_date or not left.to_date:
            continue
        for j in range(i + 1, len(rows)):
            right = rows[j]
            if (
                left.alternative_employee == right.alternative_employee
                and right.from_date
                and right.to_date
                and left.to_date >= right.from_date
                and left.from_date <= right.to_date
            ):
                frappe.throw(
                    _("Alternative Employee {0} has overlapping assignment rows ({1} and {2}).").format(
                        frappe.bold(left.alternative_employee),
                        left.idx,
                        right.idx,
                    )
                )
