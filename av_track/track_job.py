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


def _get_doc_warehouse(doc):
    warehouse = doc.set_warehouse
    if warehouse:
        return warehouse

    items = doc.items or []
    for item in items:
        item_warehouse = item.warehouse
        if item_warehouse:
            return item_warehouse

    return None


def _get_warehouse_coords(warehouse):
    if not warehouse:
        return None, None
    return frappe.db.get_value(
        "Warehouse",
        warehouse,
        ["track_pickup_lat", "track_pickup_lng"],
    )


def _get_company_coords(company):
    if not company:
        return None, None
    return frappe.db.get_value(
        "Company",
        company,
        ["track_pickup_lat", "track_pickup_lng"],
    )


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
    job.company = doc.company
    job.source_doctype = doc.doctype
    job.source_docname = doc.name
    job.customer_name = doc.customer_name or doc.customer
    job.customer_phone = doc.contact_mobile or doc.mobile_no
    job.notes = doc.remarks

    warehouse = _get_doc_warehouse(doc)
    pickup_lat, pickup_lng = _get_warehouse_coords(warehouse)
    if pickup_lat is not None and pickup_lng is not None:
        job.pickup_lat = pickup_lat
        job.pickup_lng = pickup_lng
    else:
        company_lat, company_lng = _get_company_coords(job.company)
        if company_lat is not None and company_lng is not None:
            job.pickup_lat = company_lat
            job.pickup_lng = company_lng

    job.insert(ignore_permissions=True)
