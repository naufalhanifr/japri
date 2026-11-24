import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, getJson, parseRetryAfter } from './client'

const signal = new AbortController().signal

function respond(status: number, body: unknown = {}, headers: Record<string, string> = {}) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => new Response(typeof body === 'string' ? body : JSON.stringify(body), { status, headers })),
  )
}

afterEach(() => vi.unstubAllGlobals())

describe('getJson', () => {
  it('returns parsed JSON and builds the query string', async () => {
    respond(200, { ok: true })
    await expect(getJson('/api/x', { date: '2026-11-24' }, signal)).resolves.toEqual({ ok: true })
    expect(fetch).toHaveBeenCalledWith('/api/x?date=2026-11-24', expect.objectContaining({ signal }))
  })

  it('maps 429 with Retry-After seconds', async () => {
    respond(429, '', { 'Retry-After': '12' })
    await expect(getJson('/api/x', undefined, signal)).rejects.toMatchObject({
      kind: 'rate_limited',
      status: 429,
      retryAfterMs: 12_000,
    })
  })

  it('maps 404 and uses the server message', async () => {
    respond(404, { error: { code: 'not_found', message: 'Driver tidak ada', details: null } })
    await expect(getJson('/api/x', undefined, signal)).rejects.toMatchObject({
      kind: 'not_found',
      code: 'not_found',
      message: 'Driver tidak ada',
    })
  })

  it('maps 422 to validation and 5xx to server', async () => {
    respond(422, { error: { code: 'range_too_long', message: 'x', details: null } })
    await expect(getJson('/api/x', undefined, signal)).rejects.toMatchObject({ kind: 'validation', code: 'range_too_long' })
    respond(502, '<html>bad gateway</html>')
    await expect(getJson('/api/x', undefined, signal)).rejects.toMatchObject({ kind: 'server', status: 502 })
  })

  it('maps a failed fetch to a network error but lets aborts through', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    await expect(getJson('/api/x', undefined, signal)).rejects.toMatchObject({ kind: 'network' })
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new DOMException('aborted', 'AbortError')))
    await expect(getJson('/api/x', undefined, signal)).rejects.toMatchObject({ name: 'AbortError' })
  })

  it('reports an unreadable success body as a server error', async () => {
    respond(200, 'not json')
    const error: unknown = await getJson('/api/x', undefined, signal).catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).kind).toBe('server')
  })
})

describe('parseRetryAfter', () => {
  it('handles seconds, HTTP dates, and junk', () => {
    expect(parseRetryAfter('5')).toBe(5000)
    expect(parseRetryAfter(null)).toBeNull()
    expect(parseRetryAfter('soon')).toBeNull()
    const now = Date.parse('2026-11-24T10:00:00Z')
    expect(parseRetryAfter('Tue, 24 Nov 2026 10:00:30 GMT', now)).toBe(30_000)
  })
})
