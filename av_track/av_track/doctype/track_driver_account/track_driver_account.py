from __future__ import unicode_literals

import frappe
from frappe.model.document import Document


class TrackDriverAccount(Document):
    def validate(self):
        self._validate_unique_driver_company()

    def _validate_unique_driver_company(self):
        if not self.company or not self.driver:
            return

        existing = frappe.db.exists(
            "Track Driver Account",
            {
                "company": self.company,
                "driver": self.driver,
                "name": ["!=", self.name],
            },
        )
        if existing:
            frappe.throw("Driver is already linked to this company.", title="Duplicate Driver Account")
