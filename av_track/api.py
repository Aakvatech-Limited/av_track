from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_driver_account():
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    records = frappe.get_all(
        "Track Driver Account",
        filters={"user": user},
        pluck="name",
        limit=1,
        ignore_permissions=True,
    )
    return records[0] if records else None
