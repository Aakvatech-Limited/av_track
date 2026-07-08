from __future__ import unicode_literals

import base64
import binascii

import frappe
from frappe.utils.file_manager import save_file
from frappe.utils import get_datetime, now_datetime, nowdate


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


def _get_driver_account_for_user(user):
    records = frappe.get_all(
        "Track Driver Account",
        filters={"user": user},
        fields=["name", "driver"],
        limit=1,
        ignore_permissions=True,
    )
    return records[0] if records else None


def _get_assigned_job_for_driver(job_id, driver_id):
    job = frappe.get_doc("Track Delivery Job", job_id)
    if job.assigned_driver != driver_id:
        frappe.throw("Not permitted.")
    return job


def _enforce_single_en_route_job(driver_id, current_job_name, next_status):
    if next_status != "En Route":
        return

    existing = frappe.db.exists(
        "Track Delivery Job",
        {
            "assigned_driver": driver_id,
            "status": "En Route",
            "name": ["!=", current_job_name],
        },
    )
    if existing:
        frappe.throw(
            "You already have an En Route job. Complete it before starting another."
        )


def _validate_status_transition(current_status, new_status):
    if current_status == new_status:
        return

    allowed = {
        "": {"Assigned"},
        None: {"Assigned"},
        "Assigned": {"Picked Up", "En Route", "Failed"},
        "Picked Up": {"En Route", "Failed"},
        "En Route": {"Delivered", "Failed"},
        "Delivered": set(),
        "Failed": set(),
    }
    allowed_targets = allowed.get(current_status, set())
    if new_status not in allowed_targets:
        frappe.throw(
            f"Invalid status transition from '{current_status or 'None'}' to '{new_status}'."
        )


def _set_status_timestamps(job, status, status_time):
    job.last_status_at = status_time
    if status == "Assigned" and not job.assigned_at:
        job.assigned_at = status_time
    if status == "Picked Up" and not job.picked_up_at:
        job.picked_up_at = status_time
    if status == "En Route" and not job.picked_up_at:
        # If skipping straight from Assigned to En Route in the driver UI
        job.picked_up_at = status_time
    if status == "Delivered":
        job.delivered_at = status_time


def _create_status_log(
    job_name, status, changed_by, changed_at, lat=None, lng=None, note=None
):
    log = frappe.new_doc("Track Status Log")
    log.delivery_job = job_name
    log.status = status
    log.changed_by = changed_by
    log.changed_at = changed_at
    log.lat = lat
    log.lng = lng
    log.note = note
    log.insert(ignore_permissions=True)


def _notify_driver_realtime(driver_id, event, message):
    if not driver_id:
        return
    accounts = frappe.get_all(
        "Track Driver Account",
        filters={"driver": driver_id, "is_active": 1},
        fields=["user"],
    )
    for acc in accounts:
        user = acc.get("user")
        if user:
            frappe.publish_realtime(
                event=event,
                message=message,
                user=user,
                after_commit=True
            )


def _update_job_status_and_log(job, status, changed_by, lat=None, lng=None, note=None):
    _validate_status_transition(job.status, status)
    _enforce_single_en_route_job(job.assigned_driver, job.name, status)

    status_time = now_datetime()
    job.status = status
    _set_status_timestamps(job, status, status_time)
    job.save(ignore_permissions=True)
    _create_status_log(
        job.name, status, changed_by, status_time, lat=lat, lng=lng, note=note
    )

    return status_time


def _data_url_to_attachment(
    data_url, filename, attached_to_doctype=None, attached_to_name=None
):
    if not data_url or not isinstance(data_url, str):
        return data_url
    if not data_url.startswith("data:"):
        return data_url

    try:
        header, encoded = data_url.split(",", 1)
    except ValueError:
        frappe.throw("Invalid file payload format.")

    ext = "png"
    if "image/jpeg" in header:
        ext = "jpg"
    elif "image/webp" in header:
        ext = "webp"
    elif "image/svg+xml" in header:
        ext = "svg"

    try:
        binary = base64.b64decode(encoded)
    except (binascii.Error, ValueError):
        frappe.throw("Invalid base64 file data.")

    file_name = f"{filename}.{ext}"
    file_doc = save_file(
        fname=file_name,
        content=binary,
        dt=attached_to_doctype,
        dn=attached_to_name,
        is_private=0,
    )
    return file_doc.file_url


@frappe.whitelist()
def get_driver_dashboard():
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = frappe.get_all(
        "Track Driver Account",
        filters={"user": user},
        fields=["name", "driver", "is_active", "is_online"],
        limit=1,
        ignore_permissions=True,
    )
    if not account:
        return {
            "profile": None,
            "progress": {
                "assigned_total": 0,
                "delivered_total": 0,
                "remaining": 0,
                "goal": 0,
                "percent": 0,
            },
            "current_task": None,
            "upcoming_stops": [],
        }

    account = account[0]
    driver_id = account.get("driver")
    full_name = None
    if driver_id:
        full_name = frappe.db.get_value("Driver", driver_id, "full_name")

    profile = {
        "account": account.get("name"),
        "driver_id": driver_id,
        "full_name": full_name,
        "is_active": account.get("is_active"),
        "is_online": account.get("is_online"),
    }

    start = get_datetime(f"{nowdate()} 00:00:00")
    end = get_datetime(f"{nowdate()} 23:59:59")

    assigned_total = frappe.db.count(
        "Track Delivery Job",
        filters={
            "assigned_driver": driver_id,
            "creation": ["between", [start, end]],
        },
    )

    delivered_total = frappe.db.count(
        "Track Delivery Job",
        filters={
            "assigned_driver": driver_id,
            "status": "Delivered",
            "creation": ["between", [start, end]],
        },
    )

    goal = assigned_total
    remaining = max(goal - delivered_total, 0)
    percent = round((delivered_total / goal) * 100) if goal else 0

    current_task = frappe.get_all(
        "Track Delivery Job",
        filters={
            "assigned_driver": driver_id,
            "status": "En Route",
        },
        fields=[
            "name",
            "status",
            "pickup_address",
            "dropoff_address",
            "customer_name",
            "customer_phone",
            "pickup_lat",
            "pickup_lng",
            "dropoff_lat",
            "dropoff_lng",
            "scheduled_dropoff",
            "last_status_at",
            "notes",
            "source_doctype",
            "source_docname",
        ],
        order_by="modified desc",
        limit=1,
        ignore_permissions=True,
    )

    upcoming_stops = frappe.get_all(
        "Track Delivery Job",
        filters={
            "assigned_driver": driver_id,
            "status": ["in", ["Assigned", "Picked Up"]],
        },
        fields=[
            "name",
            "dropoff_address",
            "pickup_address",
            "status",
            "customer_name",
            "customer_phone",
            "last_status_at",
            "notes",
            "source_doctype",
            "source_docname",
        ],
        order_by="modified asc",
        ignore_permissions=True,
    )

    settings = frappe.get_single("Track Settings")
    map_provider = settings.map_provider
    map_api_key = settings.get_password("map_api_key") if settings else None

    # Fetch items for current task
    if current_task:
        task = current_task[0]
        task["items"] = _fetch_job_items(task.get("source_doctype"), task.get("source_docname"))

    # Fetch items for upcoming stops
    for stop in upcoming_stops:
        stop["items"] = _fetch_job_items(stop.get("source_doctype"), stop.get("source_docname"))

    return {
        "profile": profile,
        "map": {
            "provider": map_provider,
            "api_key": map_api_key,
        },
        "progress": {
            "assigned_total": assigned_total,
            "delivered_total": delivered_total,
            "remaining": remaining,
            "goal": goal,
            "percent": percent,
        },
        "current_task": current_task[0] if current_task else None,
        "upcoming_stops": upcoming_stops,
    }


def _fetch_job_items(source_doctype, source_docname):
    if not source_doctype or not source_docname:
        return []
        
    items = []
    try:
        source_doc = frappe.get_doc(source_doctype, source_docname)
        for row in source_doc.get("items", []):
            name = row.get("item_name") or row.get("item_code") or row.get("item") or "Unknown Item"
            qty = row.get("qty") or row.get("quantity") or 1
            items.append({
                "name": name,
                "qty": qty
            })
    except Exception:
        pass
    return items

@frappe.whitelist()
def set_driver_online(is_online):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = frappe.get_all(
        "Track Driver Account",
        filters={"user": user},
        fields=["name"],
        limit=1,
        ignore_permissions=True,
    )
    if not account:
        frappe.throw("Driver account not found.")

    account_name = account[0]["name"]
    online_value = 1 if str(is_online).lower() in ("1", "true", "yes", "on") else 0
    frappe.db.set_value(
        "Track Driver Account",
        account_name,
        "is_online",
        online_value,
    )
    return {"is_online": bool(online_value)}


@frappe.whitelist()
def get_job_details(job_id):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        frappe.throw("Driver account not found.")

    job = frappe.get_doc("Track Delivery Job", job_id)
    if job.assigned_driver != account["driver"]:
        frappe.throw("Not permitted.")

    return {
        "name": job.name,
        "status": job.status,
        "pickup_address": job.pickup_address,
        "pickup_lat": job.pickup_lat,
        "pickup_lng": job.pickup_lng,
        "dropoff_address": job.dropoff_address,
        "dropoff_lat": job.dropoff_lat,
        "dropoff_lng": job.dropoff_lng,
        "customer_name": job.customer_name,
        "customer_phone": job.customer_phone,
        "scheduled_pickup": job.scheduled_pickup,
        "scheduled_dropoff": job.scheduled_dropoff,
        "notes": job.notes,
    }


@frappe.whitelist()
def update_job_status(job_id, status, lat=None, lng=None, note=None):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        frappe.throw("Driver account not found.")

    job = _get_assigned_job_for_driver(job_id, account["driver"])
    _update_job_status_and_log(job, status, user, lat=lat, lng=lng, note=note)

    return {"status": job.status}


@frappe.whitelist()
def _create_pod_entry(
    job, pod_type=None, note=None, photo=None, signature=None, lat=None, lng=None
):
    photo_url = _data_url_to_attachment(
        photo,
        f"{job.name}-pod-photo",
        attached_to_doctype="Track Delivery Job",
        attached_to_name=job.name,
    )
    signature_url = _data_url_to_attachment(
        signature,
        f"{job.name}-pod-signature",
        attached_to_doctype="Track Delivery Job",
        attached_to_name=job.name,
    )

    pod = frappe.new_doc("Track Proof of Delivery")
    pod.delivery_job = job.name
    pod.pod_type = pod_type or "Signature"
    pod.recorded_at = now_datetime()
    pod.notes = note
    pod.photo = photo_url
    pod.signature = signature_url
    pod.lat = lat
    pod.lng = lng
    pod.insert(ignore_permissions=True)

    return pod


@frappe.whitelist()
def upload_pod(
    job_id, pod_type=None, note=None, photo=None, signature=None, lat=None, lng=None
):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        frappe.throw("Driver account not found.")

    job = _get_assigned_job_for_driver(job_id, account["driver"])
    pod = _create_pod_entry(
        job,
        pod_type=pod_type,
        note=note,
        photo=photo,
        signature=signature,
        lat=lat,
        lng=lng,
    )

    return {"name": pod.name}


@frappe.whitelist()
def complete_delivery(
    job_id, note=None, photo=None, signature=None, lat=None, lng=None
):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        frappe.throw("Driver account not found.")

    job = _get_assigned_job_for_driver(job_id, account["driver"])

    pod = _create_pod_entry(
        job,
        pod_type="Signature",
        note=note,
        photo=photo,
        signature=signature,
        lat=lat,
        lng=lng,
    )
    _update_job_status_and_log(job, "Delivered", user, lat=lat, lng=lng, note=note)

    return {"status": job.status, "pod": pod.name}


@frappe.whitelist()
def post_location_ping(lat, lng, accuracy=None, job_id=None, device_id=None):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        frappe.throw("Driver account not found.")

    ping = frappe.new_doc("Track Location Ping")
    ping.driver_account = account["name"]
    ping.delivery_job = job_id
    ping_time = now_datetime()
    ping.pinged_at = ping_time
    ping.lat = lat
    ping.lng = lng
    ping.accuracy = accuracy
    ping.device_id = device_id
    ping.insert(ignore_permissions=True)

    frappe.db.set_value(
        "Track Driver Account",
        account["name"],
        {
            "last_lat": lat,
            "last_lng": lng,
            "last_ping_at": ping_time,
        },
    )

    return {"name": ping.name}


@frappe.whitelist(allow_guest=True)
def get_tracking_by_token(token):
    token_doc = frappe.get_all(
        "Track Tracking Token",
        filters={"token": token, "is_active": 1},
        fields=["name", "delivery_job", "expires_at"],
        limit=1,
        ignore_permissions=True,
    )
    if not token_doc:
        frappe.throw("Invalid token.")

    token_doc = token_doc[0]
    job = frappe.get_doc("Track Delivery Job", token_doc["delivery_job"])
    logs = frappe.get_all(
        "Track Status Log",
        filters={"delivery_job": job.name},
        fields=["status", "changed_at", "lat", "lng", "note"],
        order_by="changed_at asc",
        ignore_permissions=True,
    )
    return {
        "job": {
            "name": job.name,
            "status": job.status,
            "pickup_address": job.pickup_address,
            "dropoff_address": job.dropoff_address,
            "customer_name": job.customer_name,
        },
        "logs": logs,
    }


import requests


def _get_warehouse_address(warehouse):
    """Return a human-readable address string for a warehouse."""
    if not warehouse:
        return ""
    wh = frappe.db.get_value(
        "Warehouse",
        warehouse,
        ["warehouse_name", "address_line_1", "city"],
        as_dict=True,
    )
    if not wh:
        return warehouse
    parts = [wh.get("warehouse_name") or warehouse]
    if wh.get("address_line_1"):
        parts.append(wh.get("address_line_1"))
    if wh.get("city"):
        parts.append(wh.get("city"))
    return ", ".join(p for p in parts if p)


def _get_warehouse_coords(warehouse):
    """Return (lat, lng) from custom track fields on Warehouse."""
    if not warehouse:
        return None, None
    coords = frappe.db.get_value(
        "Warehouse",
        warehouse,
        ["track_pickup_lat", "track_pickup_lng"],
    )
    if coords:
        return coords[0], coords[1]
    return None, None

def _get_supplier_coords(supplier):
    """Return (lat, lng) from custom track fields on Supplier."""
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


@frappe.whitelist()
def create_delivery_job(
    source_doctype,
    source_docname,
    company=None,
    pickup_address=None,
    pickup_lat=None,
    pickup_lng=None,
    dropoff_address=None,
    dropoff_lat=None,
    dropoff_lng=None,
    customer_name=None,
    customer_phone=None,
    notes=None,
    assigned_driver=None,
):
    """
    Generic API to create a Track Delivery Job from any source document.
    Called by amex (or any other app) — av_track stays decoupled.

    Returns the name of the created Track Delivery Job, or None if one already
    exists for this source document.
    """
    if not frappe.db.exists("DocType", "Track Delivery Job"):
        return None

    existing = frappe.db.exists(
        "Track Delivery Job",
        {"source_doctype": source_doctype, "source_docname": source_docname},
    )
    if existing:
        return existing

    job = frappe.new_doc("Track Delivery Job")
    job.company = company
    job.source_doctype = source_doctype
    job.source_docname = source_docname
    job.pickup_address = pickup_address or ""
    job.pickup_lat = pickup_lat
    job.pickup_lng = pickup_lng
    job.dropoff_address = dropoff_address or ""
    job.dropoff_lat = dropoff_lat
    job.dropoff_lng = dropoff_lng
    job.customer_name = customer_name or ""
    job.customer_phone = customer_phone or ""
    job.notes = notes or ""
    job.assigned_driver = assigned_driver
    now = now_datetime()
    job.status = "Assigned"
    job.assigned_at = now
    job.last_status_at = now
    job.insert(ignore_permissions=True)

    _create_status_log(
        job.name,
        "Assigned",
        frappe.session.user,
        now,
    )

    _notify_driver_realtime(
        assigned_driver,
        "new_delivery_job",
        {"title": "New Delivery Assigned", "job": job.name}
    )

    return job.name


@frappe.whitelist()
def complete_delivery_for_source(
    source_doctype, source_docname, note=None, lat=None, lng=None
):
    """
    Mark the Track Delivery Job for a given source document as Delivered.
    Called by amex when IBT Receipt or Purchase Receipt is submitted.

    Returns the job name if completed, None if no matching active job found.
    """
    if not frappe.db.exists("DocType", "Track Delivery Job"):
        return None

    jobs = frappe.get_all(
        "Track Delivery Job",
        filters={
            "source_doctype": source_doctype,
            "source_docname": source_docname,
            "status": ["not in", ["Delivered", "Failed"]],
        },
        pluck="name",
        limit=1,
        ignore_permissions=True,
    )
    if not jobs:
        return None

    job = frappe.get_doc("Track Delivery Job", jobs[0])

    # Walk through any missing intermediate statuses so the transition machine
    # accepts the jump straight to Delivered.
    current = job.status or ""
    walk_order = ["Assigned", "Picked Up", "En Route"]
    user = frappe.session.user
    now = now_datetime()

    for step in walk_order:
        if current == "En Route":
            break
        if current in ("", None, "Assigned"):
            _create_status_log(
                job.name, "Picked Up", user, now, note="Auto-advanced by system"
            )
            frappe.db.set_value(
                "Track Delivery Job",
                job.name,
                {
                    "status": "Picked Up",
                    "picked_up_at": now,
                    "last_status_at": now,
                },
            )
            current = "Picked Up"
        elif current == "Picked Up":
            _create_status_log(
                job.name, "En Route", user, now, note="Auto-advanced by system"
            )
            frappe.db.set_value(
                "Track Delivery Job",
                job.name,
                {
                    "status": "En Route",
                    "last_status_at": now,
                },
            )
            current = "En Route"

    # Now mark Delivered
    frappe.db.set_value(
        "Track Delivery Job",
        job.name,
        {
            "status": "Delivered",
            "delivered_at": now,
            "last_status_at": now,
        },
    )
    _create_status_log(
        job.name,
        "Delivered",
        user,
        now,
        lat=lat,
        lng=lng,
        note=note or "Auto-completed on source document submission",
    )

    # Create a minimal PoD record (note-only — photo/signature captured by driver)
    existing_pod = frappe.db.exists(
        "Track Proof of Delivery",
        {"delivery_job": job.name, "pod_type": "Note"},
    )
    if not existing_pod:
        pod = frappe.new_doc("Track Proof of Delivery")
        pod.delivery_job = job.name
        pod.pod_type = "Note"
        pod.recorded_at = now
        pod.notes = note or "Auto-completed — {0} {1}".format(
            source_doctype, source_docname
        )
        pod.lat = lat
        pod.lng = lng
        pod.insert(ignore_permissions=True)

    return job.name


@frappe.whitelist()
def geocode_address(address):
    api_key = frappe.get_doc("Track Settings").get_password("map_api_key")
    if not api_key:
        frappe.throw("Google Maps API Key is not configured in Track Settings.")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    try:
        response = requests.get(url, params={"address": address, "key": api_key})
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK" and data.get("results"):
            results = []
            for res in data["results"]:
                loc = res["geometry"]["location"]
                results.append(
                    {
                        "formatted_address": res.get("formatted_address"),
                        "lat": loc["lat"],
                        "lng": loc["lng"],
                    }
                )
            return results
        else:
            error_status = data.get("status", "Unknown Error")
            error_msg = data.get("error_message", "")
            frappe.throw(
                f"Google Maps API failed with status: {error_status}. {error_msg}"
            )
    except Exception as e:
        frappe.log_error(
            title="Google Maps Geocoding Error", message=frappe.get_traceback()
        )
        frappe.throw("Error communicating with Google Maps.")
