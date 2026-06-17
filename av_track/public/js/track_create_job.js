function add_delivery_job_button(frm) {
    if (frm.doc.docstatus === 1) {
        frm.add_custom_button(__('Track Delivery Job'), function() {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Track Delivery Job',
                    filters: {
                        source_doctype: frm.doctype,
                        source_docname: frm.doc.name
                    },
                    fieldname: 'name'
                },
                callback: function(r) {
                    if (r && r.message && r.message.name) {
                        frappe.set_route('Form', 'Track Delivery Job', r.message.name);
                    } else {
                        frappe.call({
                            method: "av_track.track_job.get_delivery_job_details",
                            args: {
                                source_doctype: frm.doctype,
                                source_docname: frm.doc.name
                            },
                            callback: function(r2) {
                                if (r2.message) {
                                    frappe.route_options = r2.message;
                                    frappe.set_route('Form', 'Track Delivery Job', 'new-track-delivery-job');
                                }
                            }
                        });
                    }
                }
            });
        }, __('Create'));
    }
}

let doctypes = [
    "Sales Order", "Sales Invoice", "Delivery Note", "POS Invoice",
    "Purchase Order", "Purchase Invoice", "Purchase Receipt"
];

doctypes.forEach(dt => {
    frappe.ui.form.on(dt, {
        refresh: function(frm) {
            add_delivery_job_button(frm);
        }
    });
});
