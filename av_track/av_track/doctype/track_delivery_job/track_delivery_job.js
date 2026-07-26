frappe.ui.form.on("Track Delivery Job", {
	assigned_driver(frm) {
		if (frm.doc.assigned_driver) {
			if (!frm.doc.status) {
				frm.set_value("status", "Assigned");
			}
		} else {
			if (frm.doc.status === "Assigned") {
				frm.set_value("status", "");
			}
		}
	}
});
