// Add Employee Documents button on refresh
frappe.ui.form.on("Employee", {
    refresh(frm) {
        // Only show after the Employee is saved (has a name)
        if (!frm.is_new()) {
            // Avoid duplicates on multiple refreshes
            frm.remove_custom_button(__("Employee Documents"));

            frm.add_custom_button(
                __("Employee Documents"),
                () => {
                    // Go to Employee Document list, filtered by this Employee
                    frappe.set_route("List", "Employee Document", { employee: frm.doc.name });
                }
            );
        }
    },

    reports_to(frm) {
        if (!frm.doc.reports_to) return;

        frappe.confirm(
            __("Would you like to update Leave Approver and Expense Approver to match Reports To?"),
            function() {
                // If Yes
                frappe.db.get_value("Employee", frm.doc.reports_to, "user_id")
                    .then(r => {
                        if (r.message && r.message.user_id) {
                            frm.set_value("leave_approver", r.message.user_id);
                            frm.set_value("expense_approver", r.message.user_id);
                            frappe.msgprint(
                                __("Leave Approver and Expense Approver updated to {0}", [r.message.user_id])
                            );
                        } else {
                            // No user_id found, show link to assign
                            frappe.msgprint({
                                message: __("The selected Reports To employee has no User ID. <a href='/app/employee/{0}'>Click here to assign a user</a>.", [frm.doc.reports_to]),
                                indicator: "red",
                                title: __("No User ID Found")
                            });
                        }
                    });
            },
            function() {
                // If No
                frappe.show_alert({ message: __("Approvers not changed"), indicator: "orange" });
            }
        );
    }
});