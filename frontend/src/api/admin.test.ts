import { afterEach, beforeEach, describe, expect, it, vi, type Mock } from 'vitest'
import { adminRequest, fetchAdminMe, loginAdmin, logoutAdmin, setCsrfToken, setSessionLostHandler } from './admin'

const json = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers })
const err = (status: number, code: string) => json({ error: { code, message: code, details: null } }, status)
const admin = { id: 1, email: 'admin@contoh.id', display_name: 'Nama' }

const lastInit = () => (vi.mocked(fetch).mock.calls.at(-1)![1] as RequestInit & { headers: Record<string, string> })

let lost: Mock<() => void>

beforeEach(() => {
  lost = vi.fn<() => void>()
  setSessionLostHandler(lost)
  setCsrfToken(null)
})

afterEach(() => {
  setSessionLostHandler(null)
  vi.unstubAllGlobals()
})

describe('adminRequest', () => {
  it('sends the CSRF token from login on POST and PATCH but not GET', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ admin, csrf_token: 'tok-1' })))
    await loginAdmin('admin@contoh.id', 'rahasia')
    expect(lastInit().headers['X-CSRF-Token']).toBeUndefined()

    vi.stubGlobal('fetch', vi.fn(async () => json({})))
    await adminRequest('/api/admin/x', { method: 'POST', body: { a: 1 } })
    expect(lastInit().headers['X-CSRF-Token']).toBe('tok-1')
    expect(lastInit().credentials).toBe('same-origin')
    expect(lastInit().body).toBe('{"a":1}')
    await adminRequest('/api/admin/x', { method: 'PATCH', body: {} })
    expect(lastInit().headers['X-CSRF-Token']).toBe('tok-1')
    await adminRequest('/api/admin/x')
    expect(lastInit().headers['X-CSRF-Token']).toBeUndefined()
  })

  it('takes a fresh token from /me', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ admin, csrf_token: 'tok-me' })))
    await expect(fetchAdminMe(new AbortController().signal)).resolves.toEqual(admin)
    vi.stubGlobal('fetch', vi.fn(async () => json({})))
    await adminRequest('/api/admin/x', { method: 'POST' })
    expect(lastInit().headers['X-CSRF-Token']).toBe('tok-me')
  })

  it('reports a lost session on 401 from an admin endpoint', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => err(401, 'session_expired')))
    await expect(adminRequest('/api/admin/drivers')).rejects.toMatchObject({ kind: 'unauthenticated' })
    expect(lost).toHaveBeenCalledTimes(1)
  })

  it('maps 403 csrf_invalid without reporting a lost session', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => err(403, 'csrf_invalid')))
    await expect(adminRequest('/api/admin/x', { method: 'POST' })).rejects.toMatchObject({ kind: 'csrf' })
    expect(lost).not.toHaveBeenCalled()
  })
})

describe('login, me, logout', () => {
  it('does not treat a wrong password as an expired session', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => err(401, 'invalid_credentials')))
    await expect(loginAdmin('a@b.id', 'x')).rejects.toMatchObject({ kind: 'unauthenticated', code: 'invalid_credentials' })
    expect(lost).not.toHaveBeenCalled()
  })

  it('exposes Retry-After on 429', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ error: { code: 'too_many_attempts', message: 'm', details: null } }, 429, { 'Retry-After': '90' })))
    await expect(loginAdmin('a@b.id', 'x')).rejects.toMatchObject({ kind: 'rate_limited', retryAfterMs: 90_000 })
  })

  it('does not treat the initial /me 401 as an expired session', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => err(401, 'unauthenticated')))
    await expect(fetchAdminMe(new AbortController().signal)).rejects.toMatchObject({ kind: 'unauthenticated' })
    expect(lost).not.toHaveBeenCalled()
  })

  it('logs out with the CSRF token and clears it afterwards', async () => {
    setCsrfToken('tok-2')
    vi.stubGlobal('fetch', vi.fn(async () => new Response(null, { status: 204 })))
    await logoutAdmin()
    expect(vi.mocked(fetch).mock.calls[0][0]).toBe('/api/admin/logout')
    expect(lastInit().method).toBe('POST')
    expect(lastInit().headers['X-CSRF-Token']).toBe('tok-2')
    vi.stubGlobal('fetch', vi.fn(async () => json({})))
    await adminRequest('/api/admin/x', { method: 'POST' })
    expect(lastInit().headers['X-CSRF-Token']).toBeUndefined()
  })

  it('treats 401 on logout as already logged out, but surfaces server errors', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => err(401, 'session_expired')))
    await expect(logoutAdmin()).resolves.toBeUndefined()
    expect(lost).not.toHaveBeenCalled()
    vi.stubGlobal('fetch', vi.fn(async () => err(500, 'internal_error')))
    await expect(logoutAdmin()).rejects.toMatchObject({ kind: 'server' })
  })
})
