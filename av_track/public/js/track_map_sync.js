frappe.provide('av_track');

av_track.open_map_picker_dialog = function(frm, lat_field, lng_field, address_field) {
    let current_lat = parseFloat(frm.doc[lat_field]) || -1.286389; // Default Nairobi coordinates if empty
    let current_lng = parseFloat(frm.doc[lng_field]) || 36.817223;
    let has_existing = Boolean(frm.doc[lat_field] && frm.doc[lng_field]);

    let d = new frappe.ui.Dialog({
        title: __('Location Map Picker'),
        size: 'large',
        fields: [
            {
                label: __('Search Location Address'),
                fieldname: 'search_address',
                fieldtype: 'Data',
                placeholder: __('Search for a street, landmark, or area...')
            },
            {
                fieldname: 'search_results',
                fieldtype: 'HTML'
            },
            {
                fieldtype: 'Section Break'
            },
            {
                fieldname: 'map_html',
                fieldtype: 'HTML'
            },
            {
                fieldtype: 'Section Break'
            },
            {
                label: __('Latitude'),
                fieldname: 'latitude',
                fieldtype: 'Float',
                precision: 8,
                read_only: 1,
                default: has_existing ? current_lat : null
            },
            {
                fieldname: 'col_break_1',
                fieldtype: 'Column Break'
            },
            {
                label: __('Longitude'),
                fieldname: 'longitude',
                fieldtype: 'Float',
                precision: 8,
                read_only: 1,
                default: has_existing ? current_lng : null
            },
            {
                fieldtype: 'Section Break'
            },
            {
                label: __('Resolved Address'),
                fieldname: 'resolved_address',
                fieldtype: 'Small Text',
                read_only: 1,
                description: __('Automatically filled in from the selected location.')
            }
        ],
        primary_action_label: __('Confirm & Save Location'),
        primary_action: function(values) {
            let lat = d.get_value('latitude');
            let lng = d.get_value('longitude');
            if (lat === null || lng === null || isNaN(lat) || isNaN(lng)) {
                frappe.msgprint(__('Please click or drag the pin on the map to select coordinates.'));
                return;
            }

            frm.set_value(lat_field, lat);
            frm.set_value(lng_field, lng);

            if (address_field) {
                let resolved = d.get_value('resolved_address');
                if (resolved) {
                    frm.set_value(address_field, resolved);
                }
            }

            let geojson = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {},
                    "geometry": { "type": "Point", "coordinates": [lng, lat] }
                }]
            };
            if (frm.fields_dict['track_geolocation']) {
                frm.set_value('track_geolocation', JSON.stringify(geojson));
            }

            frappe.show_alert({
                message: __('Coordinates saved: {0}, {1}', [lat.toFixed(6), lng.toFixed(6)]),
                indicator: 'green'
            });
            d.hide();
        }
    });

    d.show();

    let map_id = 'dialog_map_container_' + frappe.utils.get_random(6);
    d.fields_dict.map_html.$wrapper.html(
        `<div id="${map_id}" style="height: 380px; width: 100%; border-radius: 8px; border: 1px solid var(--border-color); position: relative; z-index: 1;"></div>`
    );

    let map = null;
    let marker = null;
    let search_timer = null;

    function init_leaflet_map() {
        if (typeof L === 'undefined') {
            frappe.msgprint(__('Map library is loading. Please try again in a moment.'));
            return;
        }

        let container = document.getElementById(map_id);
        if (!container) {
            setTimeout(init_leaflet_map, 100);
            return;
        }

        if (container._leaflet_id) {
            return;
        }

        let initial_zoom = has_existing ? 15 : 12;
        map = L.map(container).setView([current_lat, current_lng], initial_zoom);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        marker = L.marker([current_lat, current_lng], { draggable: true }).addTo(map);

        if (has_existing) {
            d.set_value('latitude', current_lat);
            d.set_value('longitude', current_lng);
            resolve_address_for_position(current_lat, current_lng);
        }

        // Marker drag listener
        marker.on('dragend', function(e) {
            let pos = marker.getLatLng();
            d.set_value('latitude', pos.lat);
            d.set_value('longitude', pos.lng);
            resolve_address_for_position(pos.lat, pos.lng);
        });

        // Map click listener
        map.on('click', function(e) {
            marker.setLatLng(e.latlng);
            d.set_value('latitude', e.latlng.lat);
            d.set_value('longitude', e.latlng.lng);
            resolve_address_for_position(e.latlng.lat, e.latlng.lng);
        });

        setTimeout(function() {
            if (map) {
                map.invalidateSize();
            }
        }, 300);
    }

    function update_map_position(lat, lng, zoom = 16) {
        if (!map || !marker) return;
        let new_pos = new L.LatLng(lat, lng);
        marker.setLatLng(new_pos);
        map.flyTo(new_pos, zoom);
        d.set_value('latitude', lat);
        d.set_value('longitude', lng);
    }

    function resolve_address_for_position(lat, lng) {
        frappe.call({
            method: 'av_track.api.reverse_geocode_address',
            args: { latitude: lat, longitude: lng },
            callback: function(r) {
                if (r.message && r.message.address) {
                    d.set_value('resolved_address', r.message.address);
                }
            }
        });
    }

    function render_search_results(results) {
        let $wrapper = d.fields_dict.search_results.$wrapper;
        if (!results || !results.length) {
            $wrapper.html('');
            return;
        }

        let $list = $('<div class="av-track-search-results"></div>').css({
            border: '1px solid var(--border-color)',
            'border-radius': '8px',
            'max-height': '220px',
            'overflow-y': 'auto',
            'margin-top': '4px'
        });

        results.forEach(function(result) {
            let $item = $('<div class="av-track-search-result"></div>')
                .text(result.address)
                .css({
                    padding: '8px 12px',
                    cursor: 'pointer',
                    'border-bottom': '1px solid var(--border-color)',
                    'font-size': '13px'
                })
                .on('mouseenter', function() { $(this).css('background', 'var(--bg-light-gray)'); })
                .on('mouseleave', function() { $(this).css('background', ''); })
                .on('click', function() {
                    update_map_position(result.lat, result.lng, 16);
                    d.set_value('resolved_address', result.address);
                    d.set_value('search_address', '');
                    $wrapper.html('');
                    frappe.show_alert({message: __('Location found! Drag pin to refine exact position.'), indicator: 'green'});
                });
            $list.append($item);
        });

        $wrapper.html('');
        $wrapper.append($list);
    }

    d.fields_dict.search_address.$input.on('input', function() {
        let query = ($(this).val() || '').trim();
        clearTimeout(search_timer);

        if (query.length < 3) {
            d.fields_dict.search_results.$wrapper.html('');
            return;
        }

        search_timer = setTimeout(function() {
            frappe.call({
                method: 'av_track.api.search_location',
                args: { query: query },
                callback: function(r) {
                    render_search_results(r.message || []);
                }
            });
        }, 500);
    });

    if (typeof L !== 'undefined') {
        setTimeout(init_leaflet_map, 150);
    } else {
        frappe.require([
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
        ], function() {
            setTimeout(init_leaflet_map, 150);
        });
    }
};

av_track.setup_search_button = function(frm, lat_field, lng_field, address_field) {
    frm.add_custom_button(__('Location Map Picker'), function() {
        av_track.open_map_picker_dialog(frm, lat_field, lng_field, address_field);
    }, __('Tracking'));
};

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_customer_lat', 'track_customer_lng', 'track_resolved_address');
    }
});

frappe.ui.form.on('Company', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng', 'track_resolved_address');
    }
});

frappe.ui.form.on('Warehouse', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng', 'track_resolved_address');
    }
});

frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        av_track.setup_search_button(frm, 'track_pickup_lat', 'track_pickup_lng', 'track_resolved_address');
    }
});

frappe.ui.form.on('Track Delivery Job', {
    refresh: function(frm) {
        frm.add_custom_button(__('Dropoff Location Map Picker'), function() {
            av_track.open_map_picker_dialog(frm, 'dropoff_lat', 'dropoff_lng', 'dropoff_address');
        }, __('Tracking'));

        frm.add_custom_button(__('Pickup Location Map Picker'), function() {
            av_track.open_map_picker_dialog(frm, 'pickup_lat', 'pickup_lng', 'pickup_address');
        }, __('Tracking'));
    }
});
