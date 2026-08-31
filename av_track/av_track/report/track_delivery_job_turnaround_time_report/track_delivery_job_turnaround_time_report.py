import frappe


def execute(filters=None):
    filters = filters or {}

    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw("From Date and To Date are required.")

    if frappe.utils.getdate(filters.get("from_date")) > frappe.utils.getdate(filters.get("to_date")):
        frappe.throw("From Date cannot be after To Date.")

    columns = get_columns()
    data, report_summary = get_data(filters)

    return columns, data, None, None, report_summary


def get_columns():
    return [
        {"label": "Delivery Job", "fieldname": "delivery_job", "fieldtype": "Link", "options": "Track Delivery Job", "width": 150},
        {"label": "Creation Date", "fieldname": "creation_date", "fieldtype": "Date", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": "Source Type", "fieldname": "source_doctype", "fieldtype": "Data", "width": 130},
        {"label": "Source Document", "fieldname": "source_docname", "fieldtype": "Dynamic Link", "options": "source_doctype", "width": 160},
        {"label": "Assigned Driver", "fieldname": "assigned_driver", "fieldtype": "Link", "options": "Driver", "width": 150},
        {"label": "Driver Name", "fieldname": "driver_name", "fieldtype": "Data", "width": 140},
        {"label": "Customer / Recipient", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Assigned At", "fieldname": "assigned_at", "fieldtype": "Datetime", "width": 150},
        {"label": "Picked Up At", "fieldname": "picked_up_at", "fieldtype": "Datetime", "width": 150},
        {"label": "Delivered At", "fieldname": "delivered_at", "fieldtype": "Datetime", "width": 150},
        {"label": "Pickup TAT (Mins)", "fieldname": "pickup_tat_mins", "fieldtype": "Float", "precision": 1, "width": 140},
        {"label": "Delivery TAT (Mins)", "fieldname": "delivery_tat_mins", "fieldtype": "Float", "precision": 1, "width": 140},
        {"label": "Total TAT (Mins)", "fieldname": "total_tat_mins", "fieldtype": "Float", "precision": 1, "width": 140},
        {"label": "Pickup Distance (KM)", "fieldname": "pickup_distance_km", "fieldtype": "Float", "precision": 2, "width": 140},
        {"label": "Delivery Distance (KM)", "fieldname": "delivery_distance_km", "fieldtype": "Float", "precision": 2, "width": 150},
        {"label": "Total Distance (KM)", "fieldname": "total_distance_km", "fieldtype": "Float", "precision": 2, "width": 140},
        {"label": "SLA Performance", "fieldname": "sla_performance", "fieldtype": "Data", "width": 140},
    ]


def get_data(filters):
    conds = ["tdj.creation between %(from_date)s and %(to_date)s"]
    values = {
        "from_date": f"{filters.get('from_date')} 00:00:00",
        "to_date": f"{filters.get('to_date')} 23:59:59",
    }

    if filters.get("company"):
        conds.append("tdj.company = %(company)s")
        values["company"] = filters.get("company")

    if filters.get("status"):
        conds.append("tdj.status = %(status)s")
        values["status"] = filters.get("status")

    if filters.get("assigned_driver"):
        conds.append("tdj.assigned_driver = %(assigned_driver)s")
        values["assigned_driver"] = filters.get("assigned_driver")

    if filters.get("source_doctype"):
        conds.append("tdj.source_doctype = %(source_doctype)s")
        values["source_doctype"] = filters.get("source_doctype")

    condition_sql = " and ".join(conds)

    sql_query = f"""
        select
            tdj.name as delivery_job,
            date(tdj.creation) as creation_date,
            tdj.status,
            tdj.source_doctype,
            tdj.source_docname,
            tdj.assigned_driver,
            drv.full_name as driver_name,
            tdj.customer_name,
            tdj.creation,
            tdj.assigned_at,
            tdj.picked_up_at,
            tdj.delivered_at,
            tdj.scheduled_dropoff,
            tdj.pickup_distance_km,
            tdj.delivery_distance_km,
            tdj.total_distance_km
        from `tabTrack Delivery Job` tdj
        left join `tabDriver` drv on drv.name = tdj.assigned_driver
        where {condition_sql}
        order by tdj.creation desc
    """

    rows = frappe.db.sql(sql_query, values, as_dict=True)

    result = []
    total_pickup_tat = 0.0
    total_delivery_tat = 0.0
    total_tat = 0.0
    total_distance_km = 0.0
    delivered_count = 0
    pickup_count = 0
    on_time_count = 0

    for row in rows:
        assigned_time = row.get("assigned_at") or row.get("creation")
        picked_up_time = row.get("picked_up_at")
        delivered_time = row.get("delivered_at")
        scheduled_dropoff = row.get("scheduled_dropoff")

        pickup_tat_mins = None
        if assigned_time and picked_up_time:
            pickup_tat_mins = round((frappe.utils.time_diff_in_seconds(picked_up_time, assigned_time) / 60.0), 1)
            if pickup_tat_mins >= 0:
                total_pickup_tat += pickup_tat_mins
                pickup_count += 1

        delivery_tat_mins = None
        if picked_up_time and delivered_time:
            delivery_tat_mins = round((frappe.utils.time_diff_in_seconds(delivered_time, picked_up_time) / 60.0), 1)
            if delivery_tat_mins >= 0:
                total_delivery_tat += delivery_tat_mins

        total_tat_mins = None
        if assigned_time and delivered_time:
            total_tat_mins = round((frappe.utils.time_diff_in_seconds(delivered_time, assigned_time) / 60.0), 1)
            if total_tat_mins >= 0:
                total_tat += total_tat_mins
                delivered_count += 1

        sla_perf = "Pending"
        if row.get("status") == "Delivered":
            if scheduled_dropoff and delivered_time:
                if frappe.utils.get_datetime(delivered_time) <= frappe.utils.get_datetime(scheduled_dropoff):
                    sla_perf = "On Time"
                    on_time_count += 1
                else:
                    sla_perf = "Delayed"
            else:
                sla_perf = "Completed"
                on_time_count += 1
        elif row.get("status") == "Failed":
            sla_perf = "Failed"
        elif row.get("status") in ["Picked Up", "En Route"]:
            sla_perf = "In Progress"

        total_distance_km += row.get("total_distance_km") or 0.0

        result.append({
            "delivery_job": row.get("delivery_job"),
            "creation_date": row.get("creation_date"),
            "status": row.get("status") or "Unassigned",
            "source_doctype": row.get("source_doctype"),
            "source_docname": row.get("source_docname"),
            "assigned_driver": row.get("assigned_driver"),
            "driver_name": row.get("driver_name"),
            "customer_name": row.get("customer_name"),
            "assigned_at": row.get("assigned_at"),
            "picked_up_at": row.get("picked_up_at"),
            "delivered_at": row.get("delivered_at"),
            "pickup_tat_mins": pickup_tat_mins,
            "delivery_tat_mins": delivery_tat_mins,
            "total_tat_mins": total_tat_mins,
            "pickup_distance_km": row.get("pickup_distance_km"),
            "delivery_distance_km": row.get("delivery_distance_km"),
            "total_distance_km": row.get("total_distance_km"),
            "sla_performance": sla_perf,
        })

    avg_pickup_tat = round(total_pickup_tat / pickup_count, 1) if pickup_count > 0 else 0.0
    avg_delivery_tat = round(total_delivery_tat / delivered_count, 1) if delivered_count > 0 else 0.0
    avg_total_tat = round(total_tat / delivered_count, 1) if delivered_count > 0 else 0.0
    on_time_rate = round((on_time_count / delivered_count) * 100, 1) if delivered_count > 0 else 0.0

    report_summary = [
        {"value": len(rows), "indicator": "Blue", "label": "Total Jobs", "datatype": "Int"},
        {"value": delivered_count, "indicator": "Green", "label": "Delivered Jobs", "datatype": "Int"},
        {"value": avg_pickup_tat, "indicator": "Orange", "label": "Avg Pickup TAT (Mins)", "datatype": "Float"},
        {"value": avg_delivery_tat, "indicator": "Orange", "label": "Avg Delivery TAT (Mins)", "datatype": "Float"},
        {"value": avg_total_tat, "indicator": "Blue", "label": "Avg Total TAT (Mins)", "datatype": "Float"},
        {"value": round(total_distance_km, 2), "indicator": "Purple", "label": "Total Distance Covered (KM)", "datatype": "Float"},
        {"value": on_time_rate, "indicator": "Green" if on_time_rate >= 80 else "Red", "label": "On-Time Rate (%)", "datatype": "Percent"},
    ]

    return result, report_summary
