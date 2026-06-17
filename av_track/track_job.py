from __future__ import unicode_literals

import frappe


def _get_track_settings():
    return frappe.get_single("Track Settings")


def _should_create_for_doctype(source_doctype):
    settings = _get_track_settings()
    
    doctype_map = {
        "Sales Order": "auto_create_sales_order",
        "Sales Invoice": "auto_create_sales_invoice",
        "Delivery Note": "auto_create_delivery_note",
        "POS Invoice": "auto_create_pos_invoice",
        "Purchase Order": "auto_create_purchase_order",
        "Purchase Invoice": "auto_create_purchase_invoice",
        "Purchase Receipt": "auto_create_purchase_receipt",
        "IBT Request": "auto_create_ibt_request"
    }
    
    field_name = doctype_map.get(source_doctype)
    if not field_name:
        return False
        
    return bool(settings.get(field_name))


def _get_doc_warehouse(doc):
    warehouse = doc.get("set_warehouse")
    if warehouse:
        return warehouse

    items = doc.get("items") or []
    for item in items:
        item_warehouse = item.get("warehouse")
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


def _get_supplier_coords(supplier):
    if not supplier:
        return None, None
    try:
        coords = frappe.db.get_value(
            "Supplier",
            supplier,
            ["track_pickup_lat", "track_pickup_lng"],
        )
        if coords:
            return coords[0], coords[1]
    except Exception:
        pass
    return None, None


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
    job.company = doc.get("company")
    job.source_doctype = doc.doctype
    job.source_docname = doc.name
    job.notes = doc.get("remarks")

    is_purchase = doc.doctype in ["Purchase Order", "Purchase Invoice", "Purchase Receipt"]

    if is_purchase:
        job.customer_name = doc.get("supplier_name") or doc.get("supplier")
        job.customer_phone = (
            doc.get("contact_mobile")
            or doc.get("mobile_no")
            or doc.get("contact_phone")
            or doc.get("phone")
        )
        if not job.customer_phone and doc.get("supplier"):
            try:
                job.customer_phone = frappe.db.get_value("Supplier", doc.get("supplier"), "mobile_no")
            except Exception:
                pass
                
        # For purchases, pickup is the Supplier, dropoff is the Warehouse
        pickup_lat, pickup_lng = _get_supplier_coords(doc.get("supplier"))
        if pickup_lat is not None and pickup_lng is not None:
            job.pickup_lat = pickup_lat
            job.pickup_lng = pickup_lng
            
        warehouse = _get_doc_warehouse(doc)
        dropoff_lat, dropoff_lng = _get_warehouse_coords(warehouse)
        if dropoff_lat is not None and dropoff_lng is not None:
            job.dropoff_lat = dropoff_lat
            job.dropoff_lng = dropoff_lng
        else:
            company_lat, company_lng = _get_company_coords(job.company)
            if company_lat is not None and company_lng is not None:
                job.dropoff_lat = company_lat
                job.dropoff_lng = company_lng
                
    else:
        # Sales process
        job.customer_name = doc.get("customer_name") or doc.get("customer")
        job.customer_phone = (
            doc.get("contact_mobile")
            or doc.get("mobile_no")
            or doc.get("contact_phone")
            or doc.get("phone")
        )

        if not job.customer_phone and doc.get("customer"):
            try:
                job.customer_phone = frappe.db.get_value("Customer", doc.get("customer"), "mobile_no")
            except Exception:
                pass

        # For sales, pickup is the Warehouse/Company
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
