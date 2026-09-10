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

av_track.open_assign_driver_dialog = function(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Assign Driver'),
        size: 'extra-large',
        fields: [
            {
                fieldname: 'map_html',
                fieldtype: 'HTML'
            }
        ]
    });

    d.show();

    let map_id = 'assign_driver_map_' + frappe.utils.get_random(6);
    let $wrapper = d.fields_dict.map_html.$wrapper;
    $wrapper.html(`
        <div style="position: relative; height: 65vh; min-height: 420px; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color);">
            <div id="${map_id}" style="height: 100%; width: 100%;"></div>
            <div class="assign-driver-map-loading" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: var(--fg-color); z-index: 500;">
                <span class="text-muted">${__('Loading map...')}</span>
            </div>
        </div>
    `);

    const statusColor = (driver) => {
        if (!driver.is_online) return '#94a3b8'; // offline - grey
        if (driver.assigned_orders > 0) return '#2563eb'; // on delivery - blue
        return '#16a34a'; // available - green
    };

    const statusLabel = (driver) => {
        if (!driver.is_online) return __('Offline');
        if (driver.assigned_orders > 0) return __('On Delivery');
        return __('Available');
    };

    const getInitials = (name) => {
        if (!name) return '?';
        let parts = name.trim().split(/\s+/);
        let first = parts[0] ? parts[0][0] : '';
        let second = parts[1] ? parts[1][0] : '';
        return (first + second).toUpperCase();
    };

    const assign_driver = (driver) => {
        frm.set_value('assigned_driver', driver);
        frappe.show_alert({ message: __('Driver assigned. Remember to save.'), indicator: 'green' });
        d.hide();
    };

    const init_map = (drivers) => {
        let attempts = 0;
        const MAX_ATTEMPTS = 40; // ~6s of retrying before giving up

        const show_map_error = (message) => {
            $wrapper.find('.assign-driver-map-loading').html(`
                <div style="text-align:center;">
                    <span class="text-danger">${message}</span><br>
                    <button type="button" class="btn btn-xs btn-default retry-map-btn" style="margin-top:8px;">${__('Retry')}</button>
                </div>
            `).show();
            $wrapper.find('.retry-map-btn').off('click').on('click', () => {
                $wrapper.find('.assign-driver-map-loading').show().html(`<span class="text-muted">${__('Loading map...')}</span>`);
                attempts = 0;
                draw();
            });
        };

        const draw = () => {
            attempts++;

            if (typeof L === 'undefined') {
                if (attempts > MAX_ATTEMPTS) {
                    show_map_error(__('Could not load the map library.'));
                    return;
                }
                setTimeout(draw, 150);
                return;
            }

            let container = document.getElementById(map_id);
            if (!container) {
                if (attempts > MAX_ATTEMPTS) {
                    show_map_error(__('Could not find the map container.'));
                    return;
                }
                setTimeout(draw, 150);
                return;
            }

            try {
                let center = [-1.286389, 36.817223];
                let has_dropoff = frm.doc.dropoff_lat && frm.doc.dropoff_lng;
                if (has_dropoff) {
                    center = [frm.doc.dropoff_lat, frm.doc.dropoff_lng];
                }

                let map = L.map(container).setView(center, 12);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                let bounds = [];

                if (has_dropoff) {
                    let dropoffIcon = L.divIcon({
                        className: '',
                        html: `<div style="width:18px;height:18px;border-radius:50%;background:#dc2626;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>`,
                        iconSize: [18, 18],
                        iconAnchor: [9, 9]
                    });
                    L.marker(center, { icon: dropoffIcon }).addTo(map).bindPopup(__('Dropoff Location'));
                    bounds.push(center);
                }

                drivers.forEach((driver) => {
                    if (driver.last_lat == null || driver.last_lng == null) return;

                    let pos = [driver.last_lat, driver.last_lng];
                    let icon = L.divIcon({
                        className: '',
                        html: `
                            <div style="
                                width:36px;height:36px;border-radius:50%;
                                background:${statusColor(driver)};
                                border:3px solid white;
                                box-shadow:0 2px 6px rgba(0,0,0,0.4);
                                display:flex; align-items:center; justify-content:center;
                                color:white; font-weight:700; font-size:13px; font-family:inherit;
                                cursor:pointer;
                            ">${getInitials(driver.driver_name || driver.driver)}</div>
                        `,
                        iconSize: [36, 36],
                        iconAnchor: [18, 18],
                        popupAnchor: [0, -18]
                    });

                    let marker = L.marker(pos, { icon: icon }).addTo(map);
                    marker.bindPopup(`
                        <div style="font-size:12px; min-width:150px;">
                            <b>${frappe.utils.escape_html(driver.driver_name || driver.driver)}</b><br>
                            ${statusLabel(driver)} &middot; ${driver.assigned_orders || 0} ${__('active jobs')}
                            <br>
                            <button type="button" class="btn btn-xs btn-primary map-assign-btn" style="margin-top:6px; width:100%;">${__('Assign')}</button>
                        </div>
                    `);
                    marker.on('popupopen', () => {
                        $('.leaflet-popup .map-assign-btn').off('click').on('click', () => {
                            assign_driver(driver.driver);
                        });
                    });

                    bounds.push(pos);
                });

                if (bounds.length > 1) {
                    map.fitBounds(bounds, { padding: [40, 120] });
                }

                map.whenReady(() => {
                    setTimeout(() => {
                        map.invalidateSize();
                        $wrapper.find('.assign-driver-map-loading').fadeOut(150);
                    }, 150);
                });
            } catch (e) {
                console.error('Assign Driver map error:', e);
                show_map_error(__('Something went wrong loading the map.'));
            }
        };

        // Hard fallback: never let the loading state hang forever, no matter what went wrong.
        setTimeout(() => {
            if ($wrapper.find('.assign-driver-map-loading').is(':visible')) {
                show_map_error(__('The map is taking too long to load.'));
            }
        }, 8000);

        if (typeof L !== 'undefined') {
            setTimeout(draw, 100);
        } else {
            frappe.require([
                'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
                'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
            ], function() {
                setTimeout(draw, 100);
            });
        }
    };

    frappe.call({
        method: 'av_track.api.get_fleet_overview',
        callback: function(r) {
            let drivers = r.message || [];
            init_map(drivers);
        },
        error: function() {
            $wrapper.find('.assign-driver-map-loading').html(
                `<span class="text-danger">${__('Could not load drivers.')}</span>`
            );
        }
    });
};

frappe.ui.form.on('Track Delivery Job', {
    refresh: function(frm) {
        frm.add_custom_button(__('Dropoff Location Map Picker'), function() {
            av_track.open_map_picker_dialog(frm, 'dropoff_lat', 'dropoff_lng', 'dropoff_address');
        }, __('Tracking'));

        frm.add_custom_button(__('Pickup Location Map Picker'), function() {
            av_track.open_map_picker_dialog(frm, 'pickup_lat', 'pickup_lng', 'pickup_address');
        }, __('Tracking'));

        frm.add_custom_button(__('Assign Driver'), function() {
            av_track.open_assign_driver_dialog(frm);
        }, __('Tracking'));
    }
});
