// frappe.ui.form.on("Expense Claim", {
//     onload(frm) {
//         apply_gna_filter(frm);
//     },
//     refresh(frm) {
//         apply_gna_filter(frm);
//     },
//     employee(frm) {
//         apply_gna_filter(frm);
//     }
// });

// function apply_gna_filter(frm) {
//     if (!frm.doc.employee) return;

//     frappe.db.get_value("Employee", frm.doc.employee, "is_gna_employee")
//         .then(r => {
//             if (!r.message) return;
//             let is_gna = r.message.is_gna_employee;

//             frm.fields_dict.expenses.grid.get_field("expense_type")
//                 .get_query = function() {
//                     return {
//                         filters: {
//                             is_gna_expense: is_gna ? 1 : 0
//                         }
//                     };
//                 };

//             frm.refresh_field('expenses');
//         });
// }



frappe.ui.form.on("Expense Claim", {
    onload(frm) {
        apply_gna_filter(frm);
    },
    refresh(frm) {
        apply_gna_filter(frm);
    },
    employee(frm) {
        // Optional: clear expenses if employee changes
        frm.clear_table("expenses");
        frm.refresh_field("expenses");
        apply_gna_filter(frm);
    }
});

function apply_gna_filter(frm) {
    if (!frm.doc.employee) return;

    frappe.db.get_value("Employee", frm.doc.employee, "is_gna_employee")
        .then(r => {
            if (!r.message) return;
            let is_gna = r.message.is_gna_employee;

            frm.fields_dict.expenses.grid.get_field("expense_type").get_query = function(doc, cdt, cdn) {
                return {
                    filters: {
                        is_gna_expense: is_gna ? 1 : 0
                    }
                };
            };

            // Force re-render of the grid so the filter applies
            frm.refresh_field("expenses");
        });
}
