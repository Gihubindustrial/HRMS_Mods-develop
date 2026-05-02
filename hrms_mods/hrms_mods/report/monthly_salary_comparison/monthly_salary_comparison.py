import frappe
from frappe import _
from frappe.utils import getdate
from collections import defaultdict
from datetime import datetime, timedelta  
import calendar
 
 
def execute(filters=None):
    if not filters:
        filters = {}
 
    fiscal_year = filters.get("fiscal_year")
    if not fiscal_year:
        frappe.throw(_("Fiscal Year is required"))
 
    fy = frappe.get_doc("Fiscal Year", fiscal_year)
    from_date = getdate(fy.year_start_date)
    to_date = getdate(fy.year_end_date)
 
    # Get all months within the fiscal year
    month_labels = get_all_fiscal_months(from_date, to_date)
 
    # Base filters
    conditions = {
        "docstatus": 1,
        "start_date": (">=", from_date),
        "end_date": ("<=", to_date),
    }
 
    if filters.get("employee"):
        conditions["employee"] = filters["employee"]
    if filters.get("company"):
        conditions["company"] = filters["company"]
 
    department = filters.get("department")
    if department and department.lower() not in ["all", "all departments"]:
        conditions["department"] = department
 
    # Get salary slips
    salary_slips = frappe.get_all(
        "Salary Slip",
        filters=conditions,
        fields=[
            "name",
            "employee",
            "employee_name",
            "net_pay",
            "start_date",
            "payroll_entry",
        ],
    )
 
    # Safe-guard: If no data and not summarized
    if not salary_slips and not filters.get("summarized_view"):
        return get_columns([], summarized=False), []
 
    # Get cost center mapping from Payroll Entry
    payroll_entry_names = list(
        {s["payroll_entry"] for s in salary_slips if s.get("payroll_entry")}
    )
    payroll_entry_cc_map = {}
    if payroll_entry_names:
        payroll_entries = frappe.get_all(
            "Payroll Entry",
            filters={"name": ["in", payroll_entry_names]},
            fields=["name", "cost_center"],
        )
        payroll_entry_cc_map = {
            entry.name: entry.cost_center for entry in payroll_entries
        }
 
    summarized = filters.get("summarized_view")
 
    if summarized:
        # ✅ Summarized View
        summary_data = defaultdict(lambda: {"employee_set": set(), "total_salary": 0.0})
 
        for slip in salary_slips:
            cost_center_filter = filters.get("cost_center")
            if cost_center_filter:
                pe_name = slip.get("payroll_entry")
                if not pe_name:
                    continue
                cost_center = payroll_entry_cc_map.get(pe_name)
                if not cost_center or cost_center != cost_center_filter:
                    continue
 
            month_label = getdate(slip.start_date).strftime("%b %Y")
            summary_data[month_label]["employee_set"].add(slip.employee)
            summary_data[month_label]["total_salary"] += slip.net_pay
 
        summary_result = []
        for month in month_labels:
            row = {
                "month": month,
                "number_of_employees": len(summary_data[month]["employee_set"]),
                "total_salary": summary_data[month]["total_salary"],
            }
            summary_result.append(row)
 
        return get_columns(month_labels, summarized=True), summary_result
 
    else:
        # ✅ Detailed View
        salary_data = defaultdict(lambda: defaultdict(float))
        for slip in salary_slips:
            cost_center_filter = filters.get("cost_center")
            if cost_center_filter:
                pe_name = slip.get("payroll_entry")
                if not pe_name:
                    continue
                cost_center = payroll_entry_cc_map.get(pe_name)
                if not cost_center or cost_center != cost_center_filter:
                    continue
 
            month_label = getdate(slip.start_date).strftime("%b %Y")
            emp_id = slip.employee
            emp_name = slip.employee_name
            net_pay = slip.net_pay
 
            salary_data[emp_id]["employee_name"] = emp_name
            salary_data[emp_id][month_label] += net_pay
            salary_data[emp_id]["Total"] += net_pay
 
        final_data = []
        for emp_id, salary in salary_data.items():
            row = {"employee": emp_id, "employee_name": salary.get("employee_name", "")}
            for month in month_labels:
                row[month] = salary.get(month, 0.0)
            row["Total"] = salary.get("Total", 0.0)
            final_data.append(row)
 
        return get_columns(month_labels, summarized=False), final_data
 
 
def get_columns(months, summarized=False):
    if summarized:
        return [
            {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 150},
            {
                "label": _("Number of Employees"),
                "fieldname": "number_of_employees",
                "fieldtype": "Int",
                "width": 180,
            },
            {
                "label": _("Total Net Salary"),
                "fieldname": "total_salary",
                "fieldtype": "Currency",
                "width": 180,
            },
        ]
    else:
        columns = [
            {
                "label": _("Employee"),
                "fieldname": "employee",
                "fieldtype": "Link",
                "options": "Employee",
                "width": 130,
            },
            {
                "label": _("Employee Name"),
                "fieldname": "employee_name",
                "fieldtype": "Data",
                "width": 180,
            },
        ]
        for month in months:
            columns.append(
                {
                    "label": month,
                    "fieldname": month,
                    "fieldtype": "Currency",
                    "width": 120,
                }
            )
        columns.append(
            {
                "label": _("Total"),
                "fieldname": "Total",
                "fieldtype": "Currency",
                "width": 150,
            }
        )
        return columns
 
 
def get_all_fiscal_months(start_date, end_date):
    """Return a list of month labels like 'Jul 2023', ... until end_date"""
    current = start_date
    months = []
    while current <= end_date:
        label = current.strftime("%b %Y")
        months.append(label)
        next_month = current.replace(day=28) + timedelta(days=4)  # jump to next month
        current = next_month.replace(day=1)
    return months