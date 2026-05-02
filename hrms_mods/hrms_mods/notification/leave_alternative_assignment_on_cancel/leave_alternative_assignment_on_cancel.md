### إلغاء تكليف البديل | Alternative Assignment Cancelled

#### العربية
تم إلغاء طلب الإجازة، لذلك تم إلغاء تكليفك كموظف بديل.

- رقم طلب الإجازة: **{{ doc.name }}**
- الموظف: **{{ doc.employee_name or doc.employee }}**
- الشركة: **{{ doc.company or "-" }}**
- الفترة السابقة: **{{ frappe.utils.formatdate(doc.from_date) }}** إلى **{{ frappe.utils.formatdate(doc.to_date) }}**
- الحالة الحالية: **{{ doc.status or "-" }}**

لم تعد مسؤولاً عن تغطية مهام هذا الطلب.

التوزيع السابق للتغطية:
{% for row in doc.alternative_assignments %}
- **{{ row.alternative_employee }}**: {{ frappe.utils.formatdate(row.from_date) }} → {{ frappe.utils.formatdate(row.to_date) }}
{% endfor %}

---

#### English
The leave request has been cancelled, so your alternative assignment has also been cancelled.

- Leave Application: **{{ doc.name }}**
- Employee: **{{ doc.employee_name or doc.employee }}**
- Company: **{{ doc.company or "-" }}**
- Previous Period: **{{ frappe.utils.formatdate(doc.from_date) }}** to **{{ frappe.utils.formatdate(doc.to_date) }}**
- Current Status: **{{ doc.status or "-" }}**

You are no longer required to cover work for this request.

Previous coverage split:
{% for row in doc.alternative_assignments %}
- **{{ row.alternative_employee }}**: {{ frappe.utils.formatdate(row.from_date) }} -> {{ frappe.utils.formatdate(row.to_date) }}
{% endfor %}
