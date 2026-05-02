### تم تعيينك كموظف بديل | Alternative Assignment Confirmed

#### العربية
تم تعيينك كموظف بديل عن **{{ doc.employee_name or doc.employee }}** خلال فترة الإجازة.

- رقم طلب الإجازة: **{{ doc.name }}**
- الشركة: **{{ doc.company or "-" }}**
- من تاريخ: **{{ frappe.utils.formatdate(doc.from_date) }}**
- إلى تاريخ: **{{ frappe.utils.formatdate(doc.to_date) }}**
- معتمد الإجازة: **{{ doc.leave_approver or "-" }}**

يرجى متابعة مهام الموظف خلال الفترة المذكورة.

توزيع التغطية:
{% for row in doc.alternative_assignments %}
- **{{ row.alternative_employee }}**: {{ frappe.utils.formatdate(row.from_date) }} → {{ frappe.utils.formatdate(row.to_date) }}
{% endfor %}

---

#### English
You have been assigned as an alternative employee for **{{ doc.employee_name or doc.employee }}** during the leave period.

- Leave Application: **{{ doc.name }}**
- Company: **{{ doc.company or "-" }}**
- From Date: **{{ frappe.utils.formatdate(doc.from_date) }}**
- To Date: **{{ frappe.utils.formatdate(doc.to_date) }}**
- Leave Approver: **{{ doc.leave_approver or "-" }}**

Please manage the employee's work responsibilities for the above period.

Coverage split:
{% for row in doc.alternative_assignments %}
- **{{ row.alternative_employee }}**: {{ frappe.utils.formatdate(row.from_date) }} -> {{ frappe.utils.formatdate(row.to_date) }}
{% endfor %}
