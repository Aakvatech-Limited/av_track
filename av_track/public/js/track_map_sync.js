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
        <style>
            @keyframes assign-driver-pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
            .assign-driver-pulse-dot { animation: assign-driver-pulse-dot 1.5s ease-in-out infinite; }
        </style>
        <div style="position: relative; height: 65vh; min-height: 420px; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color);">
            <div id="${map_id}" style="height: 100%; width: 100%;"></div>
            <div class="assign-driver-map-loading" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: var(--fg-color); z-index: 500;">
                <span class="text-muted">${__('Loading map...')}</span>
            </div>
        </div>
    `);

    let map = null;
    let markers = {};
    let driversById = {};

    // Delegated once, on the dialog wrapper - popup content gets replaced by
    // setPopupContent() whenever a live location/status ping arrives for a
    // driver whose popup is open, which would silently drop a listener bound
    // directly to the button (it only ever fires on the first popupopen, not
    // on later content swaps).
    $wrapper.on('click', '.map-assign-btn', function() {
        assign_driver($(this).attr('data-driver'));
    });

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

    // Keep in sync with apps/av_track/frontend/src/utils/mapMotion.js -
    // Desk JS can't import that Vite-bundled ES module, so this is a
    // deliberate duplicate of the same tween/bearing helpers.
    const tweenTokens = new WeakMap();
    const tween_marker = (marker, from, to, duration_ms) => {
        duration_ms = duration_ms || 600;
        if (!marker) return;
        let token = {};
        tweenTokens.set(marker, token);
        let start = performance.now();
        const step = (now) => {
            if (tweenTokens.get(marker) !== token) return;
            let t = Math.min(1, (now - start) / duration_ms);
            let eased = 1 - Math.pow(1 - t, 3);
            marker.setLatLng([
                from[0] + (to[0] - from[0]) * eased,
                from[1] + (to[1] - from[1]) * eased,
            ]);
            if (t < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };

    const bearing_between = (p1, p2) => {
        const to_rad = (deg) => (deg * Math.PI) / 180;
        const to_deg = (rad) => (rad * 180) / Math.PI;
        let d_lng = to_rad(p2[1] - p1[1]);
        let y = Math.sin(d_lng) * Math.cos(to_rad(p2[0]));
        let x = Math.cos(to_rad(p1[0])) * Math.sin(to_rad(p2[0])) -
            Math.sin(to_rad(p1[0])) * Math.cos(to_rad(p2[0])) * Math.cos(d_lng);
        return (to_deg(Math.atan2(y, x)) + 360) % 360;
    };

    const build_driver_icon = (driver) => {
        let color = statusColor(driver);
        let heading = driver.is_online ? driver.heading : null;
        let arrow = heading != null
            ? `<div style="position:absolute; top:-8px; left:50%; transform:translateX(-50%); width:0; height:0; border-left:5px solid transparent; border-right:5px solid transparent; border-bottom:8px solid ${color};"></div>`
            : '';

        return L.divIcon({
            className: '',
            html: `
                <div style="position:relative; width:36px; height:36px; transform: rotate(${heading || 0}deg);">
                    ${arrow}
                    <div style="
                        width:36px;height:36px;border-radius:50%;
                        background:${color};
                        border:3px solid white;
                        box-shadow:0 2px 6px rgba(0,0,0,0.4);
                        display:flex; align-items:center; justify-content:center;
                        color:white; font-weight:700; font-size:13px; font-family:inherit;
                        cursor:pointer;
                        transform: rotate(${-(heading || 0)}deg);
                    ">${getInitials(driver.driver_name || driver.driver)}</div>
                </div>
            `,
            iconSize: [36, 36],
            iconAnchor: [18, 18],
            popupAnchor: [0, -18]
        });
    };

    const driver_popup_html = (driver) => `
        <div style="min-width:220px; padding:2px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="flex-shrink:0;">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>
                <span style="font-weight:700; font-size:13px; color:#0f172a;">${frappe.utils.escape_html(driver.driver_name || driver.driver)}</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">
                <span class="${driver.is_online ? 'assign-driver-pulse-dot' : ''}" style="width:8px; height:8px; border-radius:50%; background:${statusColor(driver)}; flex-shrink:0; margin-left:4px;"></span>
                <span style="font-size:12px; color:#64748b;">${statusLabel(driver)} &middot; ${driver.assigned_orders || 0} ${__('active jobs')}</span>
            </div>
            <button type="button" class="map-assign-btn" data-driver="${frappe.utils.escape_html(driver.driver)}" style="width:100%; background:#2563eb; color:white; border:none; border-radius:10px; padding:10px 12px; font-weight:700; font-size:13px; display:flex; align-items:center; justify-content:center; gap:6px; cursor:pointer;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                    <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                ${__('Assign Driver')}
            </button>
        </div>
    `;

    const render_driver_marker = (driver) => {
        if (!map || driver.last_lat == null || driver.last_lng == null) return;

        let pos = [driver.last_lat, driver.last_lng];
        let existing = markers[driver.driver];

        if (existing) {
            let current = existing.getLatLng();
            tween_marker(existing, [current.lat, current.lng], pos);
            existing.setIcon(build_driver_icon(driver));
            existing.setPopupContent(driver_popup_html(driver));
            return;
        }

        let marker = L.marker(pos, { icon: build_driver_icon(driver) }).addTo(map);
        marker.bindPopup(driver_popup_html(driver));
        markers[driver.driver] = marker;
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

                map = L.map(container).setView(center, 12);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                let bounds = [];

                if (has_dropoff) {
                    let dropoffIcon = L.divIcon({
                        className: '',
                        html: `
                            <svg width="32" height="42" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));">
                                <path d="M16 0C7.163 0 0 7.163 0 16c0 11 16 26 16 26s16-15 16-26C32 7.163 24.837 0 16 0z" fill="#dc2626"/>
                                <circle cx="16" cy="16" r="7" fill="white"/>
                            </svg>
                        `,
                        iconSize: [32, 42],
                        iconAnchor: [16, 42],
                        popupAnchor: [0, -40]
                    });

                    let customerName = frm.doc.customer_name || __('Customer not set');
                    let customerPhone = frm.doc.customer_phone;
                    let dropoffAddress = frm.doc.dropoff_address || __('Address not set');

                    let dropoffPopupHtml = `
                        <div style="min-width:220px; padding:2px;">
                            <div style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#94a3b8; margin-bottom:8px;">${__('Dropoff')}</div>
                            <div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:10px;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="margin-top:2px; flex-shrink:0;">
                                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                                    <circle cx="12" cy="10" r="3"/>
                                </svg>
                                <span style="font-weight:700; font-size:13px; color:#0f172a;">${frappe.utils.escape_html(dropoffAddress)}</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:8px;${customerPhone ? ' margin-bottom:8px;' : ''}">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="flex-shrink:0;">
                                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                                    <circle cx="12" cy="7" r="4"/>
                                </svg>
                                <span style="font-weight:600; font-size:13px; color:#0f172a;">${frappe.utils.escape_html(customerName)}</span>
                            </div>
                            ${customerPhone ? `
                            <div style="display:flex; align-items:center; gap:8px;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="flex-shrink:0;">
                                    <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                                </svg>
                                <span style="font-size:13px; color:#0f172a;">${frappe.utils.escape_html(customerPhone)}</span>
                            </div>
                            ` : ''}
                        </div>
                    `;

                    L.marker(center, { icon: dropoffIcon }).addTo(map).bindPopup(dropoffPopupHtml);
                    bounds.push(center);
                }

                drivers.forEach((driver) => {
                    driversById[driver.driver] = driver;
                    render_driver_marker(driver);
                    if (driver.last_lat != null && driver.last_lng != null) {
                        bounds.push([driver.last_lat, driver.last_lng]);
                    }
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

                // Live updates while the dialog stays open - the only place in
                // this app that listens to Frappe's realtime socket directly.
                const on_location_update = (data) => {
                    if (!data || !data.driver) return;
                    let driver = driversById[data.driver] || { driver: data.driver };
                    let had_position = driver.last_lat != null && driver.last_lng != null;
                    let prev = had_position ? [driver.last_lat, driver.last_lng] : [data.lat, data.lng];
                    driver.driver_name = data.driver_name || driver.driver_name;
                    driver.last_lat = data.lat;
                    driver.last_lng = data.lng;
                    driver.heading = bearing_between(prev, [data.lat, data.lng]);
                    driversById[data.driver] = driver;
                    render_driver_marker(driver);
                };
                const on_status_update = (data) => {
                    if (!data || !data.driver || !driversById[data.driver]) return;
                    driversById[data.driver].is_online = data.is_online;
                    render_driver_marker(driversById[data.driver]);
                };
                frappe.realtime.on('driver_location_updated', on_location_update);
                frappe.realtime.on('driver_status_updated', on_status_update);
                d.on_hide = function() {
                    frappe.realtime.off('driver_location_updated', on_location_update);
                    frappe.realtime.off('driver_status_updated', on_status_update);
                };
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
