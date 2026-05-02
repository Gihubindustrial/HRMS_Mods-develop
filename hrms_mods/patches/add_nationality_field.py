import frappe

def execute():
    if not frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": "country"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Employee",
            "fieldname": "country",
            "label": "Nationality",
            "fieldtype": "Link",
            "options": "Nationality List",
            "insert_after": "salutation"
        }).insert()
        frappe.clear_cache(doctype="Employee")
