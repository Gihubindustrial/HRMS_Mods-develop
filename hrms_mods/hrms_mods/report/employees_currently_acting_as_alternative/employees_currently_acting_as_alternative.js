frappe.query_reports["Employees Currently Acting As Alternative"] = {
    filters: [
        {
            fieldname: "date",
            label: __("Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "alternative_employee",
            label: __("Alternative Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "employee",
            label: __("Requester Employee"),
            fieldtype: "Link",
            options: "Employee"
        }
    ]
};
