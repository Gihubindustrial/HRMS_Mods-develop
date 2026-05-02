import frappe

def execute():
    # ---- Add 'Is G&A Employee' to Employee doctype ----
    if not frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": "is_gna_employee"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Employee",
            "fieldname": "is_gna_employee",
            "label": "Is G&A Employee",
            "fieldtype": "Check",
            "insert_after": "status",  # position in Employee form
            
        }).insert(ignore_permissions=True)

    # ---- Add 'Is G&A Expense' to Expense Claim Type doctype ----
    if not frappe.db.exists("Custom Field", {"dt": "Expense Claim Type", "fieldname": "is_gna_expense"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Expense Claim Type",
            "fieldname": "is_gna_expense",
            "label": "Is G&A Expense",
            "fieldtype": "Check",
            "insert_after": "disabled",  # position in Expense Claim Type form
            
        }).insert(ignore_permissions=True)
