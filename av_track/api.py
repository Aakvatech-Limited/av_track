from __future__ import unicode_literals

import frappe
from frappe.utils import now_datetime


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


@frappe.whitelist()
def get_driver_profile():
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
        return None

    account = account[0]
    driver_id = account.get("driver")
    full_name = None
    if driver_id:
        full_name = frappe.db.get_value("Driver", driver_id, "full_name")

    return {
        "account": account.get("name"),
        "driver_id": driver_id,
        "full_name": full_name,
        "is_active": account.get("is_active"),
        "is_online": account.get("is_online"),
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
def get_assigned_jobs():
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        return []

    jobs = frappe.get_all(
        "Track Delivery Job",
        filters={
            "assigned_driver": account["driver"],
            "status": ["not in", ["Delivered", "Failed"]],
        },
        fields=[
            "name",
            "status",
            "pickup_address",
            "dropoff_address",
            "customer_name",
            "customer_phone",
            "scheduled_pickup",
            "scheduled_dropoff",
            "last_status_at",
        ],
        order_by="modified desc",
        ignore_permissions=True,
    )
    return jobs


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

    job = frappe.get_doc("Track Delivery Job", job_id)
    if job.assigned_driver != account["driver"]:
        frappe.throw("Not permitted.")

    job.status = status
    job.last_status_at = now_datetime()
    if status == "Assigned" and not job.assigned_at:
        job.assigned_at = now_datetime()
    if status == "Picked Up":
        job.picked_up_at = now_datetime()
    if status == "Delivered":
        job.delivered_at = now_datetime()
    job.save(ignore_permissions=True)

    log = frappe.new_doc("Track Status Log")
    log.delivery_job = job.name
    log.status = status
    log.changed_by = user
    log.changed_at = now_datetime()
    log.lat = lat
    log.lng = lng
    log.note = note
    log.insert(ignore_permissions=True)

    return {"status": job.status}


@frappe.whitelist()
def upload_pod(job_id, pod_type=None, note=None, photo=None, signature=None, lat=None, lng=None):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Authentication required.")

    account = _get_driver_account_for_user(user)
    if not account:
        frappe.throw("Driver account not found.")

    job = frappe.get_doc("Track Delivery Job", job_id)
    if job.assigned_driver != account["driver"]:
        frappe.throw("Not permitted.")

    pod = frappe.new_doc("Track Proof of Delivery")
    pod.delivery_job = job.name
    pod.pod_type = pod_type
    pod.recorded_at = now_datetime()
    pod.notes = note
    pod.photo = photo
    pod.signature = signature
    pod.lat = lat
    pod.lng = lng
    pod.insert(ignore_permissions=True)
    return {"name": pod.name}


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
    ping.pinged_at = now_datetime()
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
            "last_ping_at": now_datetime(),
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
