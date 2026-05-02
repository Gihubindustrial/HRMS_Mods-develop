Hello,

This is an automated reminder that the following employee document will reach its expiry date on the date shown below.

| Field | Value |
| --- | --- |
| **Employee** | {{ employee_name }} |
| **Employee ID** | {{ doc.employee }} |
| **Document type** | {{ document_type_label or "—" }} |
| **Expiry date** | {{ expiry_date_formatted }} |
| **Calendar days remaining** | {{ days_until_expiry }} |

Please open the document, verify the attachment, and plan renewal or replacement before the expiry date.

**Open in desk:** [{{ doc.name }}]({{ document_link }})

---

{% if company %}
_This message was sent automatically by the Employee Document expiry notification ({{ company }})._
{% else %}
_This message was sent automatically by the Employee Document expiry notification._
{% endif %}
