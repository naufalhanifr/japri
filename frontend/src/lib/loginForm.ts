const EMAIL_PATTERN = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/

export interface LoginErrors {
  email?: string
  password?: string
}

export function validateLogin(email: string, password: string): LoginErrors {
  const errors: LoginErrors = {}
  const trimmed = email.trim()
  if (!trimmed) errors.email = 'Email wajib diisi.'
  else if (!EMAIL_PATTERN.test(trimmed)) errors.email = 'Format email tidak valid. Contoh: nama@perusahaan.id'
  if (!password) errors.password = 'Password wajib diisi.'
  return errors
}

export function waitLabel(seconds: number): string {
  if (seconds < 60) return 'kurang dari satu menit'
  return `${Math.ceil(seconds / 60)} menit`
}

export function safeReturnPath(value: unknown): string {
  if (typeof value !== 'string' || !value.startsWith('/')) return '/'
  const url = new URL(value, window.location.origin)
  if (url.origin !== window.location.origin || url.pathname.startsWith('/masuk')) return '/'
  return url.pathname + url.search
}
