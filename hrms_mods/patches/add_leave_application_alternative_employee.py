import frappe


def _delete_legacy_single_alternative_fields():
    for fieldname in ("alternative_employee", "alternative_employee_user", "alternative_employee_email"):
        custom_field_name = frappe.db.get_value(
            "Custom Field", {"dt": "Leave Application", "fieldname": fieldname}, "name"
        )
        if custom_field_name:
            frappe.delete_doc("Custom Field", custom_field_name, force=1, ignore_permissions=True)


def execute():
    _delete_legacy_single_alternative_fields()

    if not frappe.db.exists("Custom Field", {"dt": "Leave Application", "fieldname": "alternative_assignments"}):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Leave Application",
                "fieldname": "alternative_assignments",
                "label": "Alternative Assignments",
                "fieldtype": "Table",
                "options": "Leave Alternative Assignment",
                "insert_after": "leave_approver",
            }
        ).insert(ignore_permissions=True)

    if not frappe.db.exists(
        "Custom Field", {"dt": "Leave Application", "fieldname": "alternative_assignment_emails"}
    ):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Leave Application",
                "fieldname": "alternative_assignment_emails",
                "label": "Alternative Assignment Emails",
                "fieldtype": "Data",
                "read_only": 1,
                "hidden": 1,
                "insert_after": "alternative_assignments",
            }
        ).insert(ignore_permissions=True)
