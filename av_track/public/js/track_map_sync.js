frappe.provide('av_track');

av_track.sync_geolocation = function(frm, lat_field, lng_field) {
    if (frm.doc.track_geolocation) {
        try {
            let geo = JSON.parse(frm.doc.track_geolocation);
            if (geo.features && geo.features.length > 0) {
                let coords = geo.features[0].geometry.coordinates;
                // GeoJSON coordinates are [Longitude, Latitude]
                frm.set_value(lng_field, coords[0]);
                frm.set_value(lat_field, coords[1]);
            }
        } catch(e) {
            console.error("Error parsing geolocation", e);
        }
    } else {
        frm.set_value(lng_field, null);
        frm.set_value(lat_field, null);
    }
};

frappe.ui.form.on('Customer', {
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_customer_lat', 'track_customer_lng');
    }
});

frappe.ui.form.on('Company', {
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});

frappe.ui.form.on('Warehouse', {
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});

frappe.ui.form.on('Supplier', {
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});
