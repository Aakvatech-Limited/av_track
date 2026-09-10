const activeTweens = new Map()

// Glides a marker from its current position to a new one instead of
// snapping, so a live location push reads as movement, not a refresh.
// Tokened per-marker so a second ping arriving mid-glide cancels the
// stale animation instead of fighting it for the same marker.
export const tweenMarker = (marker, fromLatLng, toLatLng, durationMs = 600) => {
  if (!marker) return

  const token = Symbol('tween')
  activeTweens.set(marker, token)

  const start = performance.now()
  const [fromLat, fromLng] = fromLatLng
  const [toLat, toLng] = toLatLng

  const step = (now) => {
    if (activeTweens.get(marker) !== token) return

    const t = Math.min(1, (now - start) / durationMs)
    const eased = 1 - Math.pow(1 - t, 3)
    marker.setLatLng([
      fromLat + (toLat - fromLat) * eased,
      fromLng + (toLng - fromLng) * eased,
    ])

    if (t < 1) {
      requestAnimationFrame(step)
    } else {
      activeTweens.delete(marker)
    }
  }

  requestAnimationFrame(step)
}

// Great-circle initial bearing in degrees from point 1 to point 2.
export const bearingBetween = ([lat1, lng1], [lat2, lng2]) => {
  const toRad = (d) => (d * Math.PI) / 180
  const toDeg = (r) => (r * 180) / Math.PI
  const dLng = toRad(lng2 - lng1)
  const y = Math.sin(dLng) * Math.cos(toRad(lat2))
  const x =
    Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
    Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(dLng)
  return (toDeg(Math.atan2(y, x)) + 360) % 360
}
