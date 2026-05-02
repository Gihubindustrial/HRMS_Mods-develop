app_name = "hrms_mods"
app_title = "HRMS Mods"
app_publisher = "takamol"
app_description = "HRMS Mods"
app_email = "info@takamol.io"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "hrms_mods",
# 		"logo": "/assets/hrms_mods/logo.png",
# 		"title": "HRMS Mods",
# 		"route": "/hrms_mods",
# 		"has_permission": "hrms_mods.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hrms_mods/css/hrms_mods.css"
# app_include_js = "/assets/hrms_mods/js/hrms_mods.js"

# include js, css files in header of web template
# web_include_css = "/assets/hrms_mods/css/hrms_mods.css"
# web_include_js = "/assets/hrms_mods/js/hrms_mods.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hrms_mods/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}


# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hrms_mods/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hrms_mods.utils.jinja_methods",
# 	"filters": "hrms_mods.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hrms_mods.install.before_install"
# after_install = "hrms_mods.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hrms_mods.uninstall.before_uninstall"
# after_uninstall = "hrms_mods.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hrms_mods.utils.before_app_install"
# after_app_install = "hrms_mods.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hrms_mods.utils.before_app_uninstall"
# after_app_uninstall = "hrms_mods.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hrms_mods.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hrms_mods.tasks.all"
# 	],
# 	"daily": [
# 		"hrms_mods.tasks.daily"
# 	],
# 	"hourly": [
# 		"hrms_mods.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hrms_mods.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hrms_mods.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hrms_mods.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hrms_mods.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hrms_mods.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hrms_mods.utils.before_request"]
# after_request = ["hrms_mods.utils.after_request"]

# Job Events
# ----------
# before_job = ["hrms_mods.utils.before_job"]
# after_job = ["hrms_mods.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hrms_mods.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
#override_doctype_class = {
#    "Payroll Entry": "hrms_mods.overrides.payroll_entry.CustomPayrollEntry"
#}




fixtures = ["Nationality List",]

# patches
patches = [
    "hrms_mods.patches.add_nationality_field.execute",
    "hrms_mods.patches.add_gna_fields.execute",
    "hrms_mods.patches.add_leave_application_alternative_employee.execute",
]


doctype_js = {
    "Full and Final Statement": "public/js/full_and_final_statement.js",
    "Employee": "public/js/employee_bundle.js",
    "Expense Claim": "public/js/expense_claim_gna_filter.js",
    "Leave Application": "public/js/leave_application_alternative.js",
}

doc_events = {
    "Leave Application": {
        "validate": "hrms_mods.hrms_mods.leave_alternative.validators.validate_alternative_employee",
        "before_submit": "hrms_mods.hrms_mods.leave_alternative.validators.validate_alternative_employee",
    }
}

# Seed / ensure common HR employee document types exist.
after_migrate = ["hrms_mods.hrms_mods.utils.seed_employee_document_types.after_migrate"]