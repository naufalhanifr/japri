export type ApiErrorKind = 'network' | 'rate_limited' | 'not_found' | 'validation' | 'server'

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

export async function getJson<T>(
  path: string,
  params: Record<string, string> | undefined,
  signal: AbortSignal,
): Promise<T> {
  const query = params && Object.keys(params).length > 0 ? `?${new URLSearchParams(params)}` : ''
  let response: Response
  try {
    response = await fetch(`${path}${query}`, { signal, headers: { Accept: 'application/json' } })
  } catch (error) {
    if (isAbortError(error)) throw error
    throw new ApiError('network', 'Tidak bisa terhubung ke server.')
  }

  if (response.ok) {
    try {
      return (await response.json()) as T
    } catch {
      throw new ApiError('server', 'Balasan server tidak bisa dibaca.', { status: response.status })
    }
  }

  const { code, message } = await readErrorBody(response)
  const options = { status: response.status, code: code ?? undefined }
  if (response.status === 429) {
    const retryAfterMs = parseRetryAfter(response.headers.get('Retry-After')) ?? undefined
    throw new ApiError('rate_limited', message ?? 'Terlalu banyak permintaan.', { ...options, retryAfterMs })
  }
  if (response.status === 404) throw new ApiError('not_found', message ?? 'Data tidak ditemukan.', options)
  if (response.status === 422 || response.status === 400) {
    throw new ApiError('validation', message ?? 'Permintaan tidak valid.', options)
  }
  throw new ApiError('server', message ?? 'Server sedang bermasalah.', options)
}
