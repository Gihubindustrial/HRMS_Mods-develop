frappe.ui.form.on("Leave Application", {
    setup(frm) {
        if (frm.fields_dict.alternative_assignments) {
            frm.set_query("alternative_employee", "alternative_assignments", () => {
                const filters = {
                    status: "Active",
                    name: ["!=", frm.doc.employee || ""]
                };

                if (frm.doc.company) {
                    filters.company = frm.doc.company;
                }

                return { filters };
            });
        }
    },

    employee(frm) {
        (frm.doc.alternative_assignments || []).forEach((row) => {
            if (row.alternative_employee && row.alternative_employee === frm.doc.employee) {
                frappe.model.set_value(row.doctype, row.name, "alternative_employee", null);
            }
        });
    },

    from_date(frm) {
        apply_default_assignment_dates(frm);
    },

    to_date(frm) {
        apply_default_assignment_dates(frm);
    },

    alternative_assignments_add(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row) return;

        if (!row.from_date && frm.doc.from_date) {
            frappe.model.set_value(cdt, cdn, "from_date", frm.doc.from_date);
        }
        if (!row.to_date && frm.doc.to_date) {
            frappe.model.set_value(cdt, cdn, "to_date", frm.doc.to_date);
        }
    }
});

function apply_default_assignment_dates(frm) {
    const rows = frm.doc.alternative_assignments || [];
    if (rows.length !== 1) {
        return;
    }

    const row = rows[0];
    if (!row) return;

    if (!row.from_date && frm.doc.from_date) {
        frappe.model.set_value(row.doctype, row.name, "from_date", frm.doc.from_date);
    }
    if (!row.to_date && frm.doc.to_date) {
        frappe.model.set_value(row.doctype, row.name, "to_date", frm.doc.to_date);
    }
}
