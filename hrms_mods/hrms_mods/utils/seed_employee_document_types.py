# Copyright (c) 2026, takamol and contributors
# For license information, please see license.txt

import frappe


def seed_employee_document_types():
	"""
	Idempotently insert default employee document types (Saudi Arabia common).
	"""
	default_types = [
		{
			"type_name": "Passport",
			"description": "Valid passport of the employee.",
			"has_expiry_date": 1,
		},
		{
			"type_name": "Iqama (Residence Permit)",
			"description": "Saudi residency permit (Iqama).",
			"has_expiry_date": 1,
		},
		{
			"type_name": "Saudi Visa",
			"description": "Saudi visa / entry visa.",
			"has_expiry_date": 1,
		},
		{
			"type_name": "Work Permit",
			"description": "Saudi work permit / employment permit.",
			"has_expiry_date": 1,
		},
		{
			"type_name": "Medical Insurance",
			"description": "Employer/partner medical insurance document.",
			"has_expiry_date": 1,
		},
		{
			"type_name": "Saudi National ID",
			"description": "Saudi national ID / identity document (where applicable).",
			"has_expiry_date": 0,
		},
		{
			"type_name": "Educational Certificate",
			"description": "Highest education certificate (degree/diploma).",
			"has_expiry_date": 0,
		},
		{
			"type_name": "Experience Certificate",
			"description": "Previous employment experience certificate(s).",
			"has_expiry_date": 0,
		},
		{
			"type_name": "CV / Resume",
			"description": "Employee CV or resume.",
			"has_expiry_date": 0,
		},
		{
			"type_name": "No Objection Certificate (NOC)",
			"description": "NOC / clearance letter (transfer/re-hiring use).",
			"has_expiry_date": 0,
		},
	]

	inserted = []
	for row in default_types:
		if frappe.db.exists("Employee Document Type", {"type_name": row["type_name"]}):
			continue

		doc = frappe.get_doc(
			{
				"doctype": "Employee Document Type",
				"type_name": row["type_name"],
				"description": row.get("description"),
				"has_expiry_date": int(row.get("has_expiry_date", 0)),
			}
		)
		doc.insert(ignore_permissions=True)
		inserted.append(row["type_name"])
	return inserted


def after_migrate():
	# Run after every migrate to ensure seed data exists.
	seed_employee_document_types()

