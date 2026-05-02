import frappe
from frappe.utils import date_diff, format_date, get_url_to_form, getdate, today


def get_context(context):
	doc = context.get("doc")
	if not doc:
		return {}

	out = {}

	if doc.employee:
		out["employee_name"] = (
			frappe.db.get_value("Employee", doc.employee, "employee_name") or doc.employee
		)
	else:
		out["employee_name"] = ""

	if doc.document_type:
		out["document_type_label"] = (
			frappe.db.get_value("Employee Document Type", doc.document_type, "type_name")
			or doc.document_type
		)
	else:
		out["document_type_label"] = ""

	if doc.get("expiry_date"):
		out["expiry_date_formatted"] = format_date(doc.expiry_date)
		out["days_until_expiry"] = date_diff(getdate(doc.expiry_date), getdate(today()))
	else:
		out["expiry_date_formatted"] = ""
		out["days_until_expiry"] = None

	out["document_link"] = get_url_to_form(doc.doctype, doc.name)
	out["company"] = (frappe.defaults.get_defaults() or {}).get("company") or ""

	return out
