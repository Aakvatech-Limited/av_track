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
        frappe.throw("You already have an En Route job. Complete it before starting another.")


def _validate_status_transition(current_status, new_status):
    if current_status == new_status:
        return

    allowed = {
        "": {"Assigned"},
        None: {"Assigned"},
        "Assigned": {"Picked Up", "Failed"},
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
    if status == "Picked Up":
        job.picked_up_at = status_time
    if status == "Delivered":
        job.delivered_at = status_time


def _create_status_log(job_name, status, changed_by, changed_at, lat=None, lng=None, note=None):
    log = frappe.new_doc("Track Status Log")
    log.delivery_job = job_name
    log.status = status
    log.changed_by = changed_by
    log.changed_at = changed_at
    log.lat = lat
    log.lng = lng
    log.note = note
    log.insert(ignore_permissions=True)


def _update_job_status_and_log(job, status, changed_by, lat=None, lng=None, note=None):
    _validate_status_transition(job.status, status)
    _enforce_single_en_route_job(job.assigned_driver, job.name, status)

    status_time = now_datetime()
    job.status = status
    _set_status_timestamps(job, status, status_time)
    job.save(ignore_permissions=True)
    _create_status_log(job.name, status, changed_by, status_time, lat=lat, lng=lng, note=note)

    return status_time


def _data_url_to_attachment(data_url, filename, attached_to_doctype=None, attached_to_name=None):
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
        ],
        order_by="modified desc",
        limit=1,
        ignore_permissions=True,
    )

    upcoming_stops = frappe.get_all(
        "Track Delivery Job",
        filters={
            "assigned_driver": driver_id,
            "status": "Picked Up",
        },
        fields=[
            "name",
            "dropoff_address",
            "pickup_address",
            "status",
            "customer_name",
            "customer_phone",
            "last_status_at",
        ],
        order_by="modified asc",
        ignore_permissions=True,
    )

    settings = frappe.get_single("Track Settings")
    map_provider = settings.map_provider
    map_api_key = settings.get_password("map_api_key") if settings else None

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
def _create_pod_entry(job, pod_type=None, note=None, photo=None, signature=None, lat=None, lng=None):
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
def upload_pod(job_id, pod_type=None, note=None, photo=None, signature=None, lat=None, lng=None):
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
def complete_delivery(job_id, note=None, photo=None, signature=None, lat=None, lng=None):
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
