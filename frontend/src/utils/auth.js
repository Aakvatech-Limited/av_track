const buildFormBody = (payload) => {
  const body = new URLSearchParams()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null) return
    if (typeof value === 'object') {
      body.append(key, JSON.stringify(value))
    } else {
      body.append(key, value)
    }
  })
  return body
}

const withCsrf = (headers = {}) => {
  if (typeof window !== 'undefined' && window.csrf_token) {
    return {
      ...headers,
      'X-Frappe-CSRF-Token': window.csrf_token,
    }
  }
  return headers
}

const request = async (url, options = {}) => {
  const response = await fetch(url, {
    credentials: 'include',
    ...options,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Request failed')
  }

  const data = await response.json()
  if (data && data.exc) {
    throw new Error(data._error_message || 'Request failed')
  }
  return data
}

export const login = async (usr, pwd) => {
  return request('/api/method/login', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
    body: buildFormBody({ usr, pwd }),
  })
}

export const logout = async () => {
  return request('/api/method/logout', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
  })
}

export const getLoggedUser = async () => {
  const data = await request('/api/method/frappe.auth.get_logged_user')
  return data.message
}

export const getDriverAccount = async (user) => {
  const data = await request('/api/method/av_track.api.get_driver_account', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
    body: buildFormBody({ user }),
  })
  return data.message
}

export const setDriverOnline = async (isOnline) => {
  const data = await request('/api/method/av_track.api.set_driver_online', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
    body: buildFormBody({ is_online: isOnline ? 1 : 0 }),
  })
  return data.message
}

export const getDriverDashboard = async () => {
  const data = await request('/api/method/av_track.api.get_driver_dashboard', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
  })
  return data.message
}

export const getJobDetails = async (jobId) => {
  const data = await request('/api/method/av_track.api.get_job_details', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
    body: buildFormBody({ job_id: jobId }),
  })
  return data.message
}

export const updateJobStatus = async (jobId, status, payload = {}) => {
  const data = await request('/api/method/av_track.api.update_job_status', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
    body: buildFormBody({
      job_id: jobId,
      status,
      lat: payload.lat,
      lng: payload.lng,
      note: payload.note,
    }),
  })
  return data.message
}

export const uploadPod = async (jobId, payload = {}) => {
  const data = await request('/api/method/av_track.api.upload_pod', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
    body: buildFormBody({
      job_id: jobId,
      pod_type: payload.podType,
      note: payload.note,
      photo: payload.photo,
      signature: payload.signature,
      lat: payload.lat,
      lng: payload.lng,
    }),
  })
  return data.message
}
