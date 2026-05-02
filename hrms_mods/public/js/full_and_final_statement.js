frappe.ui.form.on('Full and Final Statement', {
	refresh(frm) {
		// your code here
	}
});


frappe.ui.form.on('Full and Final Statement', {
    total_payable_amount: function(frm) {
        calculate_custom_total(frm);  // Trigger calculation when total_payable_amount changes
    },
    total_receivable_amount: function(frm) {
        calculate_custom_total(frm);  // Trigger calculation when total_receivable_amount changes
    }
});

function calculate_custom_total(frm) {
    if (frm.doc.total_payable_amount !== undefined && frm.doc.total_receivable_amount !== undefined) {
        let custom_total = frm.doc.total_payable_amount - frm.doc.total_receivable_amount;
        frm.set_value('custom_total_amount', custom_total);  // Update the custom field with calculated value
        frm.refresh_field('custom_total_amount');  // Refresh to reflect changes on the form
    }
}
