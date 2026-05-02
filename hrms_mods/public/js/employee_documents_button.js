// frappe.ui.form.on("Employee", {
//     refresh(frm) {
//         // Only show after the Employee is saved (has a name)
//         if (!frm.is_new()) {
//             // Avoid duplicates on multiple refreshes
//             frm.remove_custom_button(__("Employee Documents"), __("Actions"));

//             frm.add_custom_button(
//                 __("Employee Documents"),
//                 () => {
//                     // Go to Employee Document list, filtered by this Employee
//                     frappe.set_route("List", "Employee Document", { employee: frm.doc.name });
//                 },
//                 __("Actions") // groups it beside the primary actions area
//             );
//         }
//     }
// });
