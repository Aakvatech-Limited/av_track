from __future__ import unicode_literals

import json
import urllib.parse
import urllib.request
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


def fetch_google_driving_distance(lat1, lng1, lat2, lng2):
    if lat1 is None or lng1 is None or lat2 is None or lng2 is None:
        return 0.0

    try:
        api_key = frappe.db.get_single_value("Track Settings", "map_api_key")
        if not api_key:
            return 0.0

        origins = f"{lat1},{lng1}"
        destinations = f"{lat2},{lng2}"
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json?"
            f"origins={urllib.parse.quote(origins)}&"
            f"destinations={urllib.parse.quote(destinations)}&"
            f"mode=driving&key={urllib.parse.quote(api_key)}"
        )

        req = urllib.request.Request(url, headers={"User-Agent": "Frappe-AVTrack"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status") == "OK" and data.get("rows"):
            elements = data["rows"][0].get("elements", [])
            if elements and elements[0].get("status") == "OK":
                distance_meters = elements[0]["distance"]["value"]
                return round(flt(distance_meters) / 1000.0, 2)
    except Exception:
        frappe.log_error(title="AV Track Google Distance API Error", message=frappe.get_traceback())

    return 0.0


class TrackDeliveryJob(Document):
    def validate(self):
        self._sync_driver_assignment_status()
        self._set_status_timestamps()
        self._sync_distances()

    def _sync_driver_assignment_status(self):
        if self.assigned_driver:
            if not self.status:
                self.status = "Assigned"
        else:
            if self.status in ["Assigned", "Accepted"]:
                self.status = ""
                self.assigned_at = None

    def _set_status_timestamps(self):
        if not self.status:
            return

        status_changed = self.is_new() or self.has_value_changed("status")
        if not status_changed:
            return

        status_time = now_datetime()

        if self.status in ["Assigned", "Accepted"] and not self.assigned_at:
            self.assigned_at = status_time
        elif self.status in ["Picked Up", "En Route to Delivery"] and not self.picked_up_at:
            self.picked_up_at = status_time
        elif self.status == "Delivered":
            self.delivered_at = status_time

        self.last_status_at = status_time

    def _sync_distances(self):
        # Calculate Pickup distance on Picked Up or En Route to Delivery
        if self.status in ["Picked Up", "En Route to Delivery", "Delivered"] and not self.pickup_distance_km:
            driver_lat, driver_lng = None, None
            if self.assigned_driver:
                driver_lat = frappe.db.get_value("Track Driver Account", self.assigned_driver, "last_lat")
                driver_lng = frappe.db.get_value("Track Driver Account", self.assigned_driver, "last_lng")

            if driver_lat and driver_lng and self.pickup_lat and self.pickup_lng:
                self.pickup_distance_km = fetch_google_driving_distance(
                    driver_lat, driver_lng, self.pickup_lat, self.pickup_lng
                )

        # Calculate Delivery distance on Delivered
        if self.status == "Delivered" and not self.delivery_distance_km:
            if self.pickup_lat and self.pickup_lng and self.dropoff_lat and self.dropoff_lng:
                self.delivery_distance_km = fetch_google_driving_distance(
                    self.pickup_lat, self.pickup_lng, self.dropoff_lat, self.dropoff_lng
                )

        # Total distance
        p_dist = flt(self.pickup_distance_km)
        d_dist = flt(self.delivery_distance_km)
        if p_dist > 0 or d_dist > 0:
            self.total_distance_km = round(p_dist + d_dist, 2)

