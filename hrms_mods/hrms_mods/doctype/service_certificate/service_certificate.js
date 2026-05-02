// Copyright (c) 2025, takamol and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Service Certificate", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Service Certificate', {
    refresh: function(frm) {
        // Optional: You can add form-level validations or UI tweaks here
    },
    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Employee",
                    name: frm.doc.employee
                },
                callback: function(r) {
                    if (r.message) {
                        let employee = r.message;
                        let status = employee.status ? employee.status.toLowerCase() : "";

                        // Validate employee status
                        if (status !== "left") {
                            frappe.msgprint(
                                __("Cannot create a Service Certificate for an active employee. Current status: {0}", [employee.status || "Not Set"])
                            );
                            frm.set_value('employee', '');
                            return;
                        }

                        // Optionally, set joining_date and relieving_date if not set
                        if (!frm.doc.joining_date && employee.date_of_joining) {
                            frm.set_value('joining_date', employee.date_of_joining);
                        }
                        if (!frm.doc.relieving_date && employee.relieving_date) {
                            frm.set_value('relieving_date', employee.relieving_date);
                        }

                        // Check for existing certificates
                        frappe.call({
                            method: "frappe.client.get_list",
                            args: {
                                doctype: "Service Certificate",
                                fields: ["name"],
                                filters: {
                                    employee: frm.doc.employee,
                                    joining_date: frm.doc.joining_date,
                                    relieving_date: frm.doc.relieving_date,
                                    name: ["!=", frm.doc.name] // Exclude current doc in case of edit
                                },
                                limit_page_length: 1
                            },
                            callback: function(res) {
                                if (res.message && res.message.length > 0) {
                                    frappe.msgprint(
                                        __("A Service Certificate has already been issued for this employee during the period from {0} to {1}.", [
                                            frappe.datetime.str_to_user(frm.doc.joining_date),
                                            frappe.datetime.str_to_user(frm.doc.relieving_date)
                                        ])
                                    );
                                    frm.set_value('employee', '');
                                }
                            }
                        });
                    }
                }
            });
        }
    },
    // Optionally, validate joining_date and relieving_date changes
    joining_date: function(frm) {
        validate_period(frm);
    },
    relieving_date: function(frm) {
        validate_period(frm);
    }
});

function validate_period(frm) {
    if (frm.doc.employee && frm.doc.joining_date && frm.doc.relieving_date) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Service Certificate",
                fields: ["name"],
                filters: {
                    employee: frm.doc.employee,
                    joining_date: frm.doc.joining_date,
                    relieving_date: frm.doc.relieving_date,
                    name: ["!=", frm.doc.name] // Exclude current doc in case of edit
                },
                limit_page_length: 1
            },
            callback: function(res) {
                if (res.message && res.message.length > 0) {
                    frappe.msgprint(
                        __("A Service Certificate has already been issued for this employee during the period from {0} to {1}.", [
                            frappe.datetime.str_to_user(frm.doc.joining_date),
                            frappe.datetime.str_to_user(frm.doc.relieving_date)
                        ])
                    );
                    // Optionally, clear the date fields or prevent form submission
                }
            }
        });
    }
}
