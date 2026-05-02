frappe.ui.form.on("Excuse for Attendance", {
    refresh(frm) {
        // Auto-fill leave approver when form loads (if employee is set)
        if (frm.doc.employee && !frm.doc.leave_approver) {
            populate_leave_approver(frm);
        }
    },

    employee(frm) {
        // 1. Check employee status instantly
        if (frm.doc.employee) {
            frappe.db.get_value("Employee", frm.doc.employee, "status")
                .then(r => {
                    if (r.message && r.message.status) {
                        if (r.message.status.toLowerCase() !== "active") {
                            frappe.msgprint({
                                title: __("Not Allowed"),
                                message: __("Selected employee is not active."),
                                indicator: "red"
                            });
                            frm.set_value("employee", null);
                        }
                    }
                });

            // 2. Auto-fill leave approver instantly
            populate_leave_approver(frm);
        }
    },

    date(frm) {
        check_duplicate(frm);
    },

    from_time(frm) {
        check_duplicate(frm);
    },

    to_time(frm) {
        check_duplicate(frm);
    }
});

// Helper: Populate leave approver from Employee
function populate_leave_approver(frm) {
    frappe.db.get_value("Employee", frm.doc.employee, "leave_approver")
        .then(r => {
            if (r.message && r.message.leave_approver) {
                frm.set_value("leave_approver", r.message.leave_approver);
            }
        });
}

// Helper: Check for duplicate instantly
function check_duplicate(frm) {
    if (frm.doc.employee && frm.doc.date && frm.doc.from_time && frm.doc.to_time) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Excuse for Attendance",
                filters: {
                    employee: frm.doc.employee,
                    date: frm.doc.date,
                    from_time: frm.doc.from_time,
                    to_time: frm.doc.to_time
                },
                fields: ["name"],
                limit: 1
            },
            callback: function(r) {
                if (r.message && r.message.length > 0 && r.message[0].name !== frm.doc.name) {
                    frappe.msgprint({
                        title: __("Duplicate Found"),
                        message: __("An excuse already exists for this employee with the same date and time."),
                        indicator: "red"
                    });
                }
            }
        });
    }
}
