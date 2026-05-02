frappe.ui.form.on("Employee Penalty", {
	onload(frm) {
		frm.set_query("penalty_type", function () {
			return {
				filters: {
					type: "Deduction",
				},
			};
		});
	},

	date(frm) {
		if (!frm.doc.payroll_date) {
			frm.set_value("payroll_date", frm.doc.date);
		}
	},
});
