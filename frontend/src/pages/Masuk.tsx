import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { Banner } from '../components/Banner'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'
import { usePageTitle } from '../hooks/usePageTitle'
import { safeReturnPath, validateLogin, waitLabel, type LoginErrors } from '../lib/loginForm'

type Failure =
  | { kind: 'invalid' }
  | { kind: 'rate_limited'; until: number | null }
  | { kind: 'failed' }

export function Masuk() {
  usePageTitle('Login Admin')
  const { state, login } = useAuth()
  const location = useLocation()
  const locationState = (location.state ?? {}) as { from?: unknown; expired?: unknown }
  const returnTo = safeReturnPath(locationState.from)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<LoginErrors>({})
  const [failure, setFailure] = useState<Failure | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [now, setNow] = useState(() => Date.now())
  const emailRef = useRef<HTMLInputElement>(null)
  const passwordRef = useRef<HTMLInputElement>(null)
  const ids = { email: useId(), password: useId() }

  useEffect(() => {
    emailRef.current?.focus()
  }, [])

  const waitUntil = failure?.kind === 'rate_limited' ? failure.until : null
  const waitSeconds = waitUntil === null ? 0 : Math.max(0, Math.ceil((waitUntil - now) / 1000))
  const locked = waitUntil !== null && waitSeconds > 0

  useEffect(() => {
    if (!locked) return
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [locked])

  if (state.status === 'admin') return <Navigate to={returnTo} replace />

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (submitting || locked) return
    const found = validateLogin(email, password)
    setErrors(found)
    if (found.email || found.password) {
      const target = found.email ? emailRef : passwordRef
      target.current?.focus()
      return
    }
    setFailure(null)
    setSubmitting(true)
    try {
      await login(email.trim(), password)
    } catch (error) {
      setPassword('')
      const at = Date.now()
      setNow(at)
      if (error instanceof ApiError && error.kind === 'rate_limited') {
        setFailure({ kind: 'rate_limited', until: error.retryAfterMs === null ? null : at + error.retryAfterMs })
      } else if (error instanceof ApiError && error.code === 'invalid_credentials') {
        setFailure({ kind: 'invalid' })
        passwordRef.current?.focus()
      } else {
        setFailure({ kind: 'failed' })
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main id="main" className="page page--auth" tabIndex={-1}>
      <form className="auth-card" onSubmit={onSubmit} noValidate>
        <div>
          <h1 className="auth-card__title">Login Admin</h1>
          <p className="auth-card__lead">Khusus admin. Pegawai tidak perlu login untuk melihat jadwal.</p>
        </div>

        {locationState.expired === true && !failure && (
          <Banner tone="warning" icon="scheduled" title="Sesi berakhir, silakan login lagi.">
            Isian yang belum disimpan tidak ikut tersimpan.
          </Banner>
        )}
        {failure?.kind === 'invalid' && (
          <Banner tone="danger" title="Email atau password salah.">Periksa isian Anda, lalu coba lagi.</Banner>
        )}
        {failure?.kind === 'rate_limited' && (
          <Banner tone="danger" title="Terlalu banyak percobaan.">
            {waitUntil === null || waitSeconds > 0
              ? `Coba lagi dalam ${waitUntil === null ? 'beberapa menit' : waitLabel(waitSeconds)}.`
              : 'Anda bisa mencoba masuk lagi.'}
          </Banner>
        )}
        {failure?.kind === 'failed' && (
          <Banner tone="danger" icon="offline" title="Login belum bisa diproses.">Periksa koneksi, lalu coba lagi.</Banner>
        )}

        <div className="field">
          <label className="field__label" htmlFor={ids.email}>Email</label>
          <input
            ref={emailRef}
            id={ids.email}
            name="email"
            type="email"
            className="field__input"
            autoComplete="username"
            placeholder="nama@perusahaan.id"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-invalid={errors.email ? true : undefined}
            aria-describedby={errors.email ? `${ids.email}-error` : undefined}
          />
          {errors.email && <FieldError id={`${ids.email}-error`}>{errors.email}</FieldError>}
        </div>

        <div className="field">
          <label className="field__label" htmlFor={ids.password}>Password</label>
          <input
            ref={passwordRef}
            id={ids.password}
            name="password"
            type="password"
            className="field__input"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={errors.password ? true : undefined}
            aria-describedby={errors.password ? `${ids.password}-error` : undefined}
          />
          {errors.password && <FieldError id={`${ids.password}-error`}>{errors.password}</FieldError>}
        </div>

        <Button type="submit" variant="primary" className="btn--full" disabled={submitting || locked} aria-busy={submitting}>
          {submitting ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Memproses...
            </>
          ) : (
            'Masuk'
          )}
        </Button>
        <Link to="/" className="text-link auth-card__back">Kembali ke Dashboard</Link>
      </form>
    </main>
  )
}

function FieldError({ id, children }: { id: string; children: string }) {
  return (
    <p id={id} className="form-error">
      <Icon name="overdue" size={14} />
      <span>{children}</span>
    </p>
  )
}
