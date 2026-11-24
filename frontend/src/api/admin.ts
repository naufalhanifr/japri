import { ApiError, requestJson } from './client'
import type { AdminProfile } from './types'

interface AdminSessionBody {
  admin: AdminProfile
  csrf_token: string
}

interface AdminRequestOptions {
  method?: 'GET' | 'POST' | 'PATCH'
  params?: Record<string, string>
  body?: unknown
  signal?: AbortSignal
  // false untuk panggilan yang 401-nya bukan tanda sesi habis (login, cek sesi awal, keluar).
  sessionRequired?: boolean
}

let csrfToken: string | null = null
let onSessionLost: (() => void) | null = null

export function setCsrfToken(token: string | null) {
  csrfToken = token
}

export function setSessionLostHandler(handler: (() => void) | null) {
  onSessionLost = handler
}

// Klien bersama untuk semua route admin: cookie sesi, token CSRF di POST/PATCH, 401 -> S12, dan satu kali pemulihan 403 csrf_invalid.
export async function adminRequest<T>(path: string, options: AdminRequestOptions = {}): Promise<T> {
  const { method = 'GET', params, body, signal, sessionRequired = true } = options
  const send = () => {
    const headers: Record<string, string> = {}
    if (method !== 'GET' && csrfToken) headers['X-CSRF-Token'] = csrfToken
    return requestJson<T>(path, { method, params, body, signal, headers })
  }
  const reportIfSessionLost = (error: unknown) => {
    if (sessionRequired && error instanceof ApiError && error.kind === 'unauthenticated') onSessionLost?.()
  }
  try {
    return await send()
  } catch (error) {
    if (!(error instanceof ApiError && error.kind === 'csrf')) {
      reportIfSessionLost(error)
      throw error
    }
  }
  try {
    const session = await requestJson<AdminSessionBody>('/api/admin/me', { signal })
    csrfToken = session.csrf_token
  } catch (error) {
    reportIfSessionLost(error)
    throw error
  }
  try {
    return await send()
  } catch (error) {
    reportIfSessionLost(error)
    throw error
  }
}

export async function loginAdmin(email: string, password: string): Promise<AdminProfile> {
  const result = await adminRequest<AdminSessionBody>('/api/admin/login', {
    method: 'POST',
    body: { email, password },
    sessionRequired: false,
  })
  setCsrfToken(result.csrf_token)
  return result.admin
}

export async function fetchAdminMe(signal: AbortSignal): Promise<AdminProfile> {
  const result = await adminRequest<AdminSessionBody>('/api/admin/me', { signal, sessionRequired: false })
  setCsrfToken(result.csrf_token)
  return result.admin
}

export async function logoutAdmin(): Promise<void> {
  try {
    await adminRequest<void>('/api/admin/logout', { method: 'POST', sessionRequired: false })
  } catch (error) {
    // Sesi sudah tidak ada di server: hasil akhirnya sama dengan keluar.
    if (!(error instanceof ApiError && error.kind === 'unauthenticated')) throw error
  }
  setCsrfToken(null)
}
