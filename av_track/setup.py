from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


custom_fields = {
    "Customer": [
        {
            "fieldname": "track_location_section",
            "fieldtype": "Section Break",
            "label": "Track Location",
            "insert_after": "email_id",
        },
        {
            "fieldname": "track_geolocation",
            "fieldtype": "Geolocation",
            "label": "Location Map",
            "insert_after": "track_location_section",
        },
        {
            "fieldname": "track_customer_lat",
            "fieldtype": "Float",
            "label": "Customer Latitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_geolocation",
        },
        {
            "fieldname": "track_customer_lng",
            "fieldtype": "Float",
            "label": "Customer Longitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_customer_lat",
        },
    ],
    "Company": [
        {
            "fieldname": "track_location_section",
            "fieldtype": "Section Break",
            "label": "Track Location",
            "insert_after": "email",
        },
        {
            "fieldname": "track_geolocation",
            "fieldtype": "Geolocation",
            "label": "Location Map",
            "insert_after": "track_location_section",
        },
        {
            "fieldname": "track_pickup_lat",
            "fieldtype": "Float",
            "label": "Pickup Latitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_geolocation",
        },
        {
            "fieldname": "track_pickup_lng",
            "fieldtype": "Float",
            "label": "Pickup Longitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_pickup_lat",
        },
    ],
    "Warehouse": [
        {
            "fieldname": "track_location_section",
            "fieldtype": "Section Break",
            "label": "Track Location",
            "insert_after": "mobile_no",
        },
        {
            "fieldname": "track_geolocation",
            "fieldtype": "Geolocation",
            "label": "Location Map",
            "insert_after": "track_location_section",
        },
        {
            "fieldname": "track_pickup_lat",
            "fieldtype": "Float",
            "label": "Pickup Latitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_geolocation",
        },
        {
            "fieldname": "track_pickup_lng",
            "fieldtype": "Float",
            "label": "Pickup Longitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_pickup_lat",
        },
    ],
    "Supplier": [
        {
            "fieldname": "track_location_section",
            "fieldtype": "Section Break",
            "label": "Track Location",
            "insert_after": "email_id",
        },
        {
            "fieldname": "track_geolocation",
            "fieldtype": "Geolocation",
            "label": "Location Map",
            "insert_after": "track_location_section",
        },
        {
            "fieldname": "track_pickup_lat",
            "fieldtype": "Float",
            "label": "Pickup Latitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_geolocation",
        },
        {
            "fieldname": "track_pickup_lng",
            "fieldtype": "Float",
            "label": "Pickup Longitude",
            "precision": "8",
            "read_only": 1,
            "insert_after": "track_pickup_lat",
        },
    ],
}


def after_migrate():
    create_custom_fields(custom_fields, ignore_validate=True)
