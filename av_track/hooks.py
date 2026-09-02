app_name = "av_track"
app_title = "AV Track"
app_publisher = "Sydney Kibanga"
app_description = " "
app_email = "skibanga@aakvatech.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "av_track",
# 		"logo": "/assets/av_track/logo.png",
# 		"title": "AV Track",
# 		"route": "/av_track",
# 		"has_permission": "av_track.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/av_track/css/av_track.css"
# app_include_js = "/assets/av_track/js/av_track.js"

# include js, css files in header of web template
# web_include_css = "/assets/av_track/css/av_track.css"
# web_include_js = "/assets/av_track/js/av_track.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "av_track/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Customer": "public/js/track_map_sync.js",
    "Company": "public/js/track_map_sync.js",
    "Warehouse": "public/js/track_map_sync.js",
    "Supplier": "public/js/track_map_sync.js",
    "Track Delivery Job": "public/js/track_map_sync.js",
    "Sales Order": "public/js/track_create_job.js",
    "Sales Invoice": "public/js/track_create_job.js",
    "Delivery Note": "public/js/track_create_job.js",
    "POS Invoice": "public/js/track_create_job.js",
    "Purchase Order": "public/js/track_create_job.js",
    "Purchase Invoice": "public/js/track_create_job.js",
    "Purchase Receipt": "public/js/track_create_job.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "av_track/public/icons.svg"

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
# 	"methods": "av_track.utils.jinja_methods",
# 	"filters": "av_track.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "av_track.install.before_install"
# after_install = "av_track.install.after_install"
after_migrate = "av_track.setup.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "av_track.uninstall.before_uninstall"
# after_uninstall = "av_track.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "av_track.utils.before_app_install"
# after_app_install = "av_track.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "av_track.utils.before_app_uninstall"
# after_app_uninstall = "av_track.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "av_track.notifications.get_notification_config"

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
doc_events = {
	"Sales Order": {
		"on_submit": "av_track.track_job.create_from_source"
	},
	"POS Invoice": {
		"on_submit": "av_track.track_job.create_from_source"
	},
	"Delivery Note": {
		"on_submit": "av_track.track_job.create_from_source"
	},
	"Sales Invoice": {
		"on_submit": "av_track.track_job.create_from_source"
	},
	"Purchase Order": {
		"on_submit": "av_track.track_job.create_from_source"
	},
	"Purchase Invoice": {
		"on_submit": "av_track.track_job.create_from_source"
	},
	"Purchase Receipt": {
		"on_submit": "av_track.track_job.create_from_source"
	},
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"av_track.tasks.all"
# 	],
# 	"daily": [
# 		"av_track.tasks.daily"
# 	],
# 	"hourly": [
# 		"av_track.tasks.hourly"
# 	],
# 	"weekly": [
# 		"av_track.tasks.weekly"
# 	],
# 	"monthly": [
# 		"av_track.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "av_track.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "av_track.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "av_track.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["av_track.utils.before_request"]
# after_request = ["av_track.utils.after_request"]

# Website route rules
# -------------------

website_route_rules = [
	{"from_route": "/track/<path:app_path>", "to_route": "track"},
]

# Job Events
# ----------
# before_job = ["av_track.utils.before_job"]
# after_job = ["av_track.utils.after_job"]

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
# 	"av_track.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
