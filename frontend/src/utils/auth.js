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

export const getDriverProfile = async () => {
  const data = await request('/api/method/av_track.api.get_driver_profile', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
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

export const getDriverProgress = async () => {
  const data = await request('/api/method/av_track.api.get_driver_progress', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
  })
  return data.message
}

export const getCurrentTask = async () => {
  const data = await request('/api/method/av_track.api.get_current_task', {
    method: 'POST',
    headers: withCsrf({
      'Content-Type': 'application/x-www-form-urlencoded',
    }),
  })
  return data.message
}
