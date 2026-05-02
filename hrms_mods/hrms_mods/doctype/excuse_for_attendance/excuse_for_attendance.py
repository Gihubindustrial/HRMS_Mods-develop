# # Copyright (c) 2025, takamol and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document

# class ExcuseforAttendance(Document):
#     def validate(self):
#         self.check_duplicate()
#         self.check_employee_active()
#         self.set_leave_approver()

#     def check_duplicate(self):
#         """Ensure there is no duplicate record for the same employee/date/time"""
#         exists = frappe.db.exists(
#             "Excuse for Attendance",
#             {
#                 "employee": self.employee,
#                 "date": self.date,
#                 "from_time": self.from_time,
#                 "to_time": self.to_time
#             }
#         )
#         if exists and exists != self.name:
#             frappe.throw(
#                 f"An excuse for {self.employee} on {self.date} "
#                 f"from {self.from_time} to {self.to_time} already exists."
#             )

#     def check_employee_active(self):
#         """Ensure the employee is active"""
#         status = frappe.db.get_value("Employee", self.employee, "status")
#         if status != "Active":
#             frappe.throw(f"Employee {self.employee} is not Active.")

#     def set_leave_approver(self):
#         """Auto-fill leave approver from Employee record"""
#         if self.employee:
#             approver = frappe.db.get_value("Employee", self.employee, "leave_approver")
#             if approver:
#                 self.leave_approver = approver


import frappe
from frappe import _
from frappe.model.document import Document

class ExcuseforAttendance(Document):
    def validate(self):
        self.check_duplicate()
        self.check_employee_active()
        self.set_leave_approver()

    def check_duplicate(self):
        """Prevent duplicate Excuse for Attendance for same employee/date/time"""
        filters = {
            "employee": self.employee,
            "date": self.date,               # make sure fieldname matches your doctype
            "from_time": self.from_time,
            "to_time": self.to_time
        }

        existing = frappe.db.get_value("Excuse for Attendance", filters, "name")
        if existing and existing != self.name:
            frappe.throw(
                _(
                    "Duplicate found: {0} already exists for {1} on {2} from {3} to {4}."
                ).format(existing, self.employee, self.date, self.from_time, self.to_time)
            )

    def check_employee_active(self):
        """Ensure the selected employee is active"""
        status = frappe.db.get_value("Employee", self.employee, "status")
        if status and status.strip().lower() != "active":
            frappe.throw(_("Employee {0} is not active.").format(self.employee))

    def set_leave_approver(self):
        """Auto-fill leave approver from Employee record if empty"""
        if self.employee and not self.leave_approver:
            approver = frappe.db.get_value("Employee", self.employee, "leave_approver")
            if approver:
                self.leave_approver = approver
