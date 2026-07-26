from __future__ import unicode_literals

from frappe.model.document import Document
from frappe.utils import now_datetime


class TrackDeliveryJob(Document):
    def validate(self):
        self._sync_driver_assignment_status()
        self._set_status_timestamps()

    def _sync_driver_assignment_status(self):
        if self.assigned_driver:
            if not self.status:
                self.status = "Assigned"
        else:
            if self.status == "Assigned":
                self.status = ""
                self.assigned_at = None

    def _set_status_timestamps(self):
        if not self.status:
            return

        status_changed = self.is_new() or self.has_value_changed("status")
        if not status_changed:
            return

        status_time = now_datetime()

        if self.status == "Assigned" and not self.assigned_at:
            self.assigned_at = status_time
        elif self.status == "Picked Up" and not self.picked_up_at:
            self.picked_up_at = status_time
        elif self.status == "En Route" and not self.picked_up_at:
            self.picked_up_at = status_time
        elif self.status == "Delivered":
            self.delivered_at = status_time

        self.last_status_at = status_time
