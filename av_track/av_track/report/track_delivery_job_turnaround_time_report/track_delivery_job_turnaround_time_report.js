frappe.query_reports["Track Delivery Job Turnaround Time Report"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nAssigned\nPicked Up\nEn Route\nDelivered\nFailed",
		},
		{
			fieldname: "assigned_driver",
			label: __("Driver"),
			fieldtype: "Link",
			options: "Driver",
		},
		{
			fieldname: "source_doctype",
			label: __("Source DocType"),
			fieldtype: "Select",
			options: "\nSales Order\nPOS Invoice\nDelivery Note\nIBT Request\nPurchase Order\nSales Invoice\nPurchase Invoice\nPurchase Receipt",
		},
	]
};
