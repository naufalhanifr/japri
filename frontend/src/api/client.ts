export type ApiErrorKind = 'network' | 'rate_limited' | 'not_found' | 'validation' | 'unauthenticated' | 'csrf' | 'server'

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status: number | null
  readonly code: string | null
  readonly retryAfterMs: number | null

  constructor(
    kind: ApiErrorKind,
    message: string,
    options: { status?: number; code?: string; retryAfterMs?: number } = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = options.status ?? null
    this.code = options.code ?? null
    this.retryAfterMs = options.retryAfterMs ?? null
  }
}

export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

export function parseRetryAfter(header: string | null, now: number = Date.now()): number | null {
  if (!header) return null
  const seconds = Number(header)
  if (Number.isFinite(seconds)) return Math.max(0, seconds) * 1000
  const at = Date.parse(header)
  return Number.isNaN(at) ? null : Math.max(0, at - now)
}

async function readErrorBody(response: Response): Promise<{ code: string | null; message: string | null }> {
  try {
    const body = await response.json()
    const error = body?.error
    return {
      code: typeof error?.code === 'string' ? error.code : null,
      message: typeof error?.message === 'string' ? error.message : null,
    }
  } catch {
    return { code: null, message: null }
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH'
  params?: Record<string, string>
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}

export async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', params, body, headers, signal } = options
  const query = params && Object.keys(params).length > 0 ? `?${new URLSearchParams(params)}` : ''
  let response: Response
  try {
    response = await fetch(`${path}${query}`, {
      method,
      signal,
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...headers,
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (error) {
    if (isAbortError(error)) throw error
    throw new ApiError('network', 'Tidak bisa terhubung ke server.')
  }

  if (response.ok) {
    if (response.status === 204) return undefined as T
    try {
      return (await response.json()) as T
    } catch {
      throw new ApiError('server', 'Balasan server tidak bisa dibaca.', { status: response.status })
    }
  }

  const { code, message } = await readErrorBody(response)
  const errorOptions = { status: response.status, code: code ?? undefined }
  if (response.status === 429) {
    const retryAfterMs = parseRetryAfter(response.headers.get('Retry-After')) ?? undefined
    throw new ApiError('rate_limited', message ?? 'Terlalu banyak permintaan.', { ...errorOptions, retryAfterMs })
  }
  if (response.status === 401) throw new ApiError('unauthenticated', message ?? 'Silakan masuk terlebih dahulu.', errorOptions)
  if (response.status === 403 && code === 'csrf_invalid') {
    throw new ApiError('csrf', message ?? 'Token keamanan tidak valid.', errorOptions)
  }
  if (response.status === 404) throw new ApiError('not_found', message ?? 'Data tidak ditemukan.', errorOptions)
  if (response.status === 422 || response.status === 400) {
    throw new ApiError('validation', message ?? 'Permintaan tidak valid.', errorOptions)
  }
  throw new ApiError('server', message ?? 'Server sedang bermasalah.', errorOptions)
}

export function getJson<T>(
  path: string,
  params: Record<string, string> | undefined,
  signal: AbortSignal,
): Promise<T> {
  return requestJson<T>(path, { params, signal })
}
