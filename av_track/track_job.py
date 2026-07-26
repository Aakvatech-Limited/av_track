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


def _get_customer_coords(customer):
    if not customer:
        return None, None
    try:
        coords = frappe.db.get_value(
            "Customer",
            customer,
            ["track_customer_lat", "track_customer_lng"],
        )
        if coords:
            return coords[0], coords[1]
    except Exception:
        pass
    return None, None


def _fetch_phone_from_contact(contact_name):
    if not contact_name:
        return None
    try:
        contact = frappe.db.get_value("Contact", contact_name, ["mobile_no", "phone"], as_dict=True)
        if contact:
            return contact.get("mobile_no") or contact.get("phone")
    except Exception:
        pass
    return None


def _fetch_customer_phone(doc):
    # 1. Direct fields on source doc (Sales Order / Delivery Note / Sales Invoice)
    phone = (
        doc.get("contact_mobile")
        or doc.get("mobile_no")
        or doc.get("contact_phone")
        or doc.get("phone")
    )
    if phone:
        return phone

    # 2. Contact Person linked on source doc
    if doc.get("contact_person"):
        phone = _fetch_phone_from_contact(doc.get("contact_person"))
        if phone:
            return phone

    # 3. Customer record fields
    customer_id = doc.get("customer")
    if customer_id:
        try:
            cust = frappe.db.get_value(
                "Customer",
                customer_id,
                ["mobile_no", "phone_no", "customer_primary_contact"],
                as_dict=True,
            )
            if cust:
                if cust.get("mobile_no"):
                    return cust.get("mobile_no")
                if cust.get("phone_no"):
                    return cust.get("phone_no")
                if cust.get("customer_primary_contact"):
                    phone = _fetch_phone_from_contact(cust.get("customer_primary_contact"))
                    if phone:
                        return phone
        except Exception:
            pass

        # 4. Fallback: Search any Contact linked to this Customer
        try:
            contact_links = frappe.get_all(
                "Dynamic Link",
                filters={
                    "link_doctype": "Customer",
                    "link_name": customer_id,
                    "parenttype": "Contact",
                },
                pluck="parent",
                limit=1,
            )
            if contact_links:
                phone = _fetch_phone_from_contact(contact_links[0])
                if phone:
                    return phone
        except Exception:
            pass

    return None


def _fetch_supplier_phone(doc):
    phone = (
        doc.get("contact_mobile")
        or doc.get("mobile_no")
        or doc.get("contact_phone")
        or doc.get("phone")
    )
    if phone:
        return phone

    if doc.get("contact_person"):
        phone = _fetch_phone_from_contact(doc.get("contact_person"))
        if phone:
            return phone

    supplier_id = doc.get("supplier")
    if supplier_id:
        try:
            supp = frappe.db.get_value(
                "Supplier",
                supplier_id,
                ["mobile_no", "supplier_primary_contact"],
                as_dict=True,
            )
            if supp:
                if supp.get("mobile_no"):
                    return supp.get("mobile_no")
                if supp.get("supplier_primary_contact"):
                    phone = _fetch_phone_from_contact(supp.get("supplier_primary_contact"))
                    if phone:
                        return phone
        except Exception:
            pass

        try:
            contact_links = frappe.get_all(
                "Dynamic Link",
                filters={
                    "link_doctype": "Supplier",
                    "link_name": supplier_id,
                    "parenttype": "Contact",
                },
                pluck="parent",
                limit=1,
            )
            if contact_links:
                phone = _fetch_phone_from_contact(contact_links[0])
                if phone:
                    return phone
        except Exception:
            pass

    return None


@frappe.whitelist()
def get_delivery_job_details(source_doctype, source_docname):
    doc = frappe.get_doc(source_doctype, source_docname)
    
    details = {
        "company": doc.get("company"),
        "source_doctype": doc.doctype,
        "source_docname": doc.name,
        "notes": doc.get("remarks")
    }

    is_purchase = doc.doctype in ["Purchase Order", "Purchase Invoice", "Purchase Receipt"]

    if is_purchase:
        details["customer_name"] = doc.get("supplier_name") or doc.get("supplier")
        details["customer_phone"] = _fetch_supplier_phone(doc)
                
        # For purchases, pickup is the Supplier, dropoff is the Warehouse
        pickup_lat, pickup_lng = _get_supplier_coords(doc.get("supplier"))
        if pickup_lat is not None and pickup_lng is not None:
            details["pickup_lat"] = pickup_lat
            details["pickup_lng"] = pickup_lng
            details["pickup_address"] = doc.get("supplier")
        else:
            frappe.throw("Supplier {0} is missing tracking coordinates (Latitude/Longitude). Please set them first.".format(doc.get("supplier")))
            
        warehouse = _get_doc_warehouse(doc)
        dropoff_lat, dropoff_lng = _get_warehouse_coords(warehouse)
        if dropoff_lat is not None and dropoff_lng is not None:
            details["dropoff_lat"] = dropoff_lat
            details["dropoff_lng"] = dropoff_lng
            details["dropoff_address"] = warehouse
        else:
            company_lat, company_lng = _get_company_coords(details["company"])
            if company_lat is not None and company_lng is not None:
                details["dropoff_lat"] = company_lat
                details["dropoff_lng"] = company_lng
                details["dropoff_address"] = details["company"]
            else:
                frappe.throw("Warehouse {0} and Company {1} are both missing tracking coordinates. Please set them first.".format(warehouse or "", details["company"]))
                
    else:
        # Sales process
        details["customer_name"] = doc.get("customer_name") or doc.get("customer")
        details["customer_phone"] = _fetch_customer_phone(doc)

        # For sales, pickup is the Warehouse/Company
        warehouse = _get_doc_warehouse(doc)
        pickup_lat, pickup_lng = _get_warehouse_coords(warehouse)
        if pickup_lat is not None and pickup_lng is not None:
            details["pickup_lat"] = pickup_lat
            details["pickup_lng"] = pickup_lng
            details["pickup_address"] = warehouse
        else:
            company_lat, company_lng = _get_company_coords(details["company"])
            if company_lat is not None and company_lng is not None:
                details["pickup_lat"] = company_lat
                details["pickup_lng"] = company_lng
                details["pickup_address"] = details["company"]
            else:
                frappe.throw("Warehouse {0} and Company {1} are both missing tracking coordinates. Please set them first.".format(warehouse or "", details["company"]))
                
        # Drop-off is the Customer
        customer = doc.get("customer")
        dropoff_lat, dropoff_lng = _get_customer_coords(customer)
        if dropoff_lat is not None and dropoff_lng is not None:
            details["dropoff_lat"] = dropoff_lat
            details["dropoff_lng"] = dropoff_lng
            details["dropoff_address"] = customer
        else:
            frappe.throw("Customer {0} is missing tracking coordinates (Latitude/Longitude). Please set them first.".format(customer))
                
    return details


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

    details = get_delivery_job_details(doc.doctype, doc.name)
    job = frappe.new_doc("Track Delivery Job")
    job.update(details)
    now = frappe.utils.now_datetime()
    job.status = "Assigned"
    job.assigned_at = now
    job.last_status_at = now
    job.insert(ignore_permissions=True)

