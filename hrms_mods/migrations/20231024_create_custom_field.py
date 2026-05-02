import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_custom_fields():
    custom_fields = {
        'Full and Final Statement': [
            {
                'fieldname': 'custom_total_amount',
                'label': 'Custom Total Amount',
                'fieldtype': 'Currency',  # Use 'Currency' type for financial data
                'insert_after': 'total_receivable_amount',  # Place after the 'total_receivable_amount' field
                'read_only': 1,  # This field should be read-only since it’s calculated
                'precision': 2  # Currency field precision
            }
        ]
    }

    for doctype, fields in custom_fields.items():
        for field in fields:
            create_custom_field(doctype, field)

def execute():
    create_custom_fields()
