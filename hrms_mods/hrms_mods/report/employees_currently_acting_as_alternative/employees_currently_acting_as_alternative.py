import frappe
from frappe import _
from frappe.utils import getdate, today


def execute(filters=None):
    filters = filters or {}
    report_date = getdate(filters.get("date") or today())

    columns = [
        {"label": _("Alternative Employee"), "fieldname": "alternative_employee", "fieldtype": "Link", "options": "Employee", "width": 180},
        {"label": _("Alternative Employee Name"), "fieldname": "alternative_employee_name", "fieldtype": "Data", "width": 220},
        {"label": _("Requester Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 180},
        {"label": _("Requester Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 220},
        {"label": _("Leave Type"), "fieldname": "leave_type", "fieldtype": "Link", "options": "Leave Type", "width": 140},
        {"label": _("Coverage From Date"), "fieldname": "coverage_from_date", "fieldtype": "Date", "width": 140},
        {"label": _("Coverage To Date"), "fieldname": "coverage_to_date", "fieldtype": "Date", "width": 140},
        {"label": _("Handover Notes"), "fieldname": "handover_notes", "fieldtype": "Small Text", "width": 220},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Leave Application"), "fieldname": "leave_application", "fieldtype": "Link", "options": "Leave Application", "width": 180},
    ]

    conditions = [
        "la.docstatus < 2",
        "la.status in ('Open', 'Approved')",
        "aa.alternative_employee is not null",
        "aa.alternative_employee != ''",
        "aa.parenttype = 'Leave Application'",
        "aa.parentfield = 'alternative_assignments'",
        "aa.from_date <= %(report_date)s",
        "aa.to_date >= %(report_date)s",
    ]
    values = {"report_date": report_date}

    if filters.get("company"):
        conditions.append("la.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("alternative_employee"):
        conditions.append("aa.alternative_employee = %(alternative_employee)s")
        values["alternative_employee"] = filters["alternative_employee"]

    if filters.get("employee"):
        conditions.append("la.employee = %(employee)s")
        values["employee"] = filters["employee"]

    data = frappe.db.sql(
        f"""
        select
            aa.alternative_employee,
            alt.employee_name as alternative_employee_name,
            la.employee,
            la.employee_name,
            la.leave_type,
            aa.from_date as coverage_from_date,
            aa.to_date as coverage_to_date,
            aa.handover_notes,
            la.status,
            la.name as leave_application
        from `tabLeave Application` la
        inner join `tabLeave Alternative Assignment` aa
            on aa.parent = la.name
            and aa.parenttype = 'Leave Application'
            and aa.parentfield = 'alternative_assignments'
        left join `tabEmployee` alt on alt.name = aa.alternative_employee
        where {' and '.join(conditions)}
        order by aa.alternative_employee asc, aa.from_date asc
        """,
        values,
        as_dict=True,
    )

    return columns, data
