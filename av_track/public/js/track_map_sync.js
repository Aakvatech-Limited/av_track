frappe.provide('av_track');



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
                
                frappe.call({
                    method: 'av_track.api.geocode_address',
                    args: {
                        address: address
                    },
                    callback: function(r) {
                        if (r.message) {
                            let lat = r.message.lat;
                            let lon = r.message.lng;
                            
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
                        }
                    }
                });
            }
        });
        d.show();
    }, __('Tracking'));
};

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_customer_lat', 'track_customer_lng');
    }
});

frappe.ui.form.on('Company', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});

frappe.ui.form.on('Warehouse', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});

frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng');
    }
});
