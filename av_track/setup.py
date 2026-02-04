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
            "fieldname": "track_customer_lat",
            "fieldtype": "Float",
            "label": "Customer Latitude",
            "precision": "8",
            "insert_after": "track_location_section",
        },
        {
            "fieldname": "track_customer_lng",
            "fieldtype": "Float",
            "label": "Customer Longitude",
            "precision": "8",
            "insert_after": "track_customer_lat",
        },
    ]
}


def after_migrate():
    create_custom_fields(custom_fields, ignore_validate=True)
