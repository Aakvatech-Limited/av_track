import { io } from 'socket.io-client'

export const createTrackingSocket = () => {
  const host = window.location.hostname
  const port = window.location.port ? ':9001' : ''
  const protocol = window.location.port ? 'http' : 'https'
  const url = `${protocol}://${host}${port}/${host}`
  return io(url, { withCredentials: true, reconnectionAttempts: 5 })
}
