from __future__ import unicode_literals

from frappe.model.document import Document
from frappe.utils import now_datetime


class TrackDeliveryJob(Document):
    def validate(self):
        self._set_status_timestamps()

    def _set_status_timestamps(self):
        if not self.status:
            return

        status_changed = self.is_new() or self.has_value_changed("status")
        if not status_changed:
            return

        status_time = now_datetime()

        if self.status == "Assigned" and not self.assigned_at:
            self.assigned_at = status_time
        elif self.status == "Picked Up":
            self.picked_up_at = status_time
        elif self.status == "Delivered":
            self.delivered_at = status_time

        self.last_status_at = status_time
