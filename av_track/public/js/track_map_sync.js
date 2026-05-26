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

av_track.setup_search_button = function(frm, lat_field, lng_field) {
    frm.add_custom_button(__('Search Location'), function() {
        let d = new frappe.ui.Dialog({
            title: __('Search on Google Maps'),
            fields: [
                {
                    label: __('Address'),
                    fieldname: 'search_address',
                    fieldtype: 'Data',
                    reqd: 1
                }
            ],
            primary_action_label: __('Find & Drop Pin'),
            primary_action: function(values) {
                let address = values.search_address;
                
                frappe.db.get_single_value('Track Settings', 'map_api_key').then(api_key => {
                    if (!api_key) {
                        frappe.msgprint(__("Google Maps API Key not configured in Track Settings."));
                        d.hide();
                        return;
                    }

                    let url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${api_key}`;
                    
                    fetch(url)
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "OK" && data.results.length > 0) {
                                let location = data.results[0].geometry.location;
                                let lat = location.lat;
                                let lon = location.lng;
                                
                                frm.set_value(lat_field, lat);
                                frm.set_value(lng_field, lon);
                                
                                let geojson = {
                                    "type": "FeatureCollection",
                                    "features": [{
                                        "type": "Feature",
                                        "properties": {},
                                        "geometry": { "type": "Point", "coordinates": [lon, lat] }
                                    }]
                                };
                                frm.set_value('track_geolocation', JSON.stringify(geojson));
                                
                                frappe.show_alert({message: __("Location found & updated!"), indicator: "green"});
                                d.hide();
                            } else {
                                frappe.msgprint(__("Location not found by Google Maps. Try a different address."));
                            }
                        })
                        .catch(err => {
                            console.error(err);
                            frappe.msgprint(__("Error communicating with Google Maps."));
                        });
                });
            }
        });
        d.show();
    }, __('Tracking'));
};

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_customer_lat', 'track_customer_lng');
    },
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_customer_lat', 'track_customer_lng');
    }
});

frappe.ui.form.on('Company', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng');
    },
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});

frappe.ui.form.on('Warehouse', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng');
    },
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});

frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng');
    },
    track_geolocation: function(frm) {
        av_track.sync_geolocation(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});
