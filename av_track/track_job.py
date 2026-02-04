from __future__ import unicode_literals

import frappe


def _get_track_settings():
    return frappe.get_single("Track Settings")


def _should_create_for_doctype(source_doctype):
    settings = _get_track_settings()
    if not settings.get("auto_create_jobs"):
        return False
    if not settings.get("source_doctype"):
        return False
    return settings.get("source_doctype") == source_doctype


def create_from_source(doc, method=None):
    if not doc:
        return

    if not _should_create_for_doctype(doc.doctype):
        return

    existing = frappe.db.exists(
        "Track Delivery Job",
        {"source_doctype": doc.doctype, "source_docname": doc.name},
    )
    if existing:
        return

    job = frappe.new_doc("Track Delivery Job")
    job.company = getattr(doc, "company", None)
    job.status = "Assigned"
    job.source_doctype = doc.doctype
    job.source_docname = doc.name
    job.customer_name = getattr(doc, "customer_name", None) or getattr(doc, "customer", None)
    job.customer_phone = getattr(doc, "contact_mobile", None) or getattr(doc, "mobile_no", None)
    job.notes = getattr(doc, "remarks", None)
    job.insert(ignore_permissions=True)
