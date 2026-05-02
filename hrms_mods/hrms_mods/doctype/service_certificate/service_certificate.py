# Copyright (c) 2025, takamol and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ServiceCertificate(Document):
    def validate(self):
        self.validate_employee_selected()
        self.validate_employee_status()
        self.validate_unique_certificate()

    def validate_employee_selected(self):
        """
        Ensure that the 'employee' field is populated.
        """
        if not self.employee:
            frappe.throw(_("Please select an Employee to generate the Service Certificate."))

    def validate_employee_status(self):
        """
        Ensure that the selected employee has a status of 'Left'.
        """
        employee = frappe.get_doc("Employee", self.employee)
        if not employee.status:
            frappe.throw(_("The status of the selected employee is not set. Please update the Employee record."))

        if employee.status.lower() != "left":
            frappe.throw(
                _("Cannot create a Service Certificate for an active employee. Current status: {0}").format(employee.status)
            )

        # Optionally, populate joining_date and relieving_date if not already set
        if not self.joining_date:
            self.joining_date = employee.date_of_joining
        if not self.relieving_date:
            self.relieving_date = employee.relieving_date

        # Ensure both dates are present
        if not self.joining_date or not self.relieving_date:
            frappe.throw(
                _("Both Joining Date and Relieving Date must be set in the Service Certificate.")
            )

    def validate_unique_certificate(self):
        """
        Prevent issuing multiple certificates for the same employee and employment period.
        """
        # Query existing Service Certificates with the same employee and period
        existing_certificates = frappe.db.exists(
            "Service Certificate",
            {
                "employee": self.employee,
                "joining_date": self.joining_date,
                "relieving_date": self.relieving_date,
                # Exclude the current document in case of update
                "name": ["!=", self.name] if self.name else 1
            }
        )

        if existing_certificates:
            frappe.throw(
                _("A Service Certificate has already been issued for this employee during the period from {0} to {1}.").format(
                    frappe.utils.formatdate(self.joining_date),
                    frappe.utils.formatdate(self.relieving_date)
                )
            )
