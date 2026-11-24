import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { adminRequest, setCsrfToken } from '../api/admin'
import { App } from '../App'
import { dashboard } from '../test-fixtures'

const json = (body: unknown, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers })
const apiError = (status: number, code: string, headers: Record<string, string> = {}) =>
  json({ error: { code, message: code, details: null } }, status, headers)

const admin = { id: 1, email: 'admin@contoh.id', display_name: 'Nama Admin' }

interface Server {
  sessionActive: boolean
  login: () => Response
  calls: { method: string; path: string; csrf: string | null; body: string | null }[]
}

function stubServer(overrides: Partial<Server> = {}) {
  const server: Server = {
    sessionActive: false,
    login: () => json({ admin, csrf_token: 'csrf-abc' }),
    calls: [],
    ...overrides,
  }
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = new URL(String(input), 'http://localhost').pathname
      const headers = (init?.headers ?? {}) as Record<string, string>
      server.calls.push({
        method: init?.method ?? 'GET',
        path,
        csrf: headers['X-CSRF-Token'] ?? null,
        body: typeof init?.body === 'string' ? init.body : null,
      })
      if (path === '/api/admin/me') {
        return server.sessionActive ? json({ admin, csrf_token: 'csrf-abc' }) : apiError(401, 'unauthenticated')
      }
      if (path === '/api/admin/login') {
        const response = server.login()
        if (response.ok) server.sessionActive = true
        return response
      }
      if (path === '/api/admin/logout') {
        server.sessionActive = false
        return new Response(null, { status: 204 })
      }
      if (path.startsWith('/api/admin/')) {
        return server.sessionActive ? json({}) : apiError(401, 'session_expired')
      }
      if (path === '/api/public/dashboard') return json(dashboard())
      if (path === '/api/public/drivers') return json({ items: [] })
      return json({ items: [], page: 1, page_size: 20, total: 0 })
    }),
  )
  return server
}

function renderApp(url = '/masuk') {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <App />
    </MemoryRouter>,
  )
}

async function fillAndSubmit(email = 'admin@contoh.id', password = 'rahasia-benar') {
  const user = userEvent.setup()
  await user.type(await screen.findByLabelText('Email'), email)
  await user.type(screen.getByLabelText('Password'), password)
  await user.click(screen.getByRole('button', { name: 'Masuk' }))
  return user
}

beforeEach(() => setCsrfToken(null))
afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
  localStorage.clear()
  sessionStorage.clear()
})

describe('S4 Login admin', () => {
  it('focuses the email field and shows the public menu without admin items', async () => {
    stubServer()
    renderApp()
    expect(await screen.findByRole('heading', { name: 'Login Admin' })).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveFocus()
    expect(screen.queryByRole('link', { name: 'Booking' })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Login Admin' })).not.toBeInTheDocument()
  })

  it('blocks invalid input before calling the API', async () => {
    const server = stubServer()
    renderApp()
    const user = userEvent.setup()
    await user.type(await screen.findByLabelText('Email'), 'admin@contoh')
    await user.click(screen.getByRole('button', { name: 'Masuk' }))
    expect(screen.getByText(/Format email tidak valid/)).toBeInTheDocument()
    expect(screen.getByText('Password wajib diisi.')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInvalid()
    expect(server.calls.filter((c) => c.path === '/api/admin/login')).toHaveLength(0)
  })

  it('logs in, lands in Mode Admin, and keeps the password out of storage, URL and console', async () => {
    const consoleSpies = (['log', 'info', 'warn', 'error', 'debug'] as const).map((m) => vi.spyOn(console, m))
    const server = stubServer()
    renderApp()
    await fillAndSubmit('Admin@Contoh.id', 'rahasia-benar')

    expect(await screen.findByText('Nama Admin')).toBeInTheDocument()
    expect(screen.getByText('Admin')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Booking' })).toHaveAttribute('href', '/admin/booking')
    expect(screen.getByRole('link', { name: 'Kelola driver' })).toHaveAttribute('href', '/admin/driver')
    expect(screen.getByRole('button', { name: 'Keluar' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Login Admin' })).not.toBeInTheDocument()

    const login = server.calls.find((c) => c.path === '/api/admin/login')!
    expect(JSON.parse(login.body!)).toEqual({ email: 'Admin@Contoh.id', password: 'rahasia-benar' })

    const dump = JSON.stringify({ ...localStorage }) + JSON.stringify({ ...sessionStorage }) + window.location.href
    expect(dump).not.toContain('rahasia-benar')
    for (const spy of consoleSpies) expect(JSON.stringify(spy.mock.calls)).not.toContain('rahasia-benar')
  })

  it('shows a generic message on wrong credentials, keeps the email, clears the password', async () => {
    stubServer({ login: () => apiError(401, 'invalid_credentials') })
    renderApp()
    await fillAndSubmit('admin@contoh.id', 'salah-sekali')

    expect(await screen.findByText('Email atau password salah.')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveValue('admin@contoh.id')
    expect(screen.getByLabelText('Password')).toHaveValue('')
    expect(screen.getByLabelText('Password')).toHaveFocus()
    expect(screen.queryByText('Nama Admin')).not.toBeInTheDocument()
  })

  it('shows the wait time from Retry-After on 429 and locks the button until it passes', async () => {
    stubServer({ login: () => apiError(429, 'too_many_attempts', { 'Retry-After': '120' }) })
    renderApp()
    await fillAndSubmit()

    expect(await screen.findByText('Terlalu banyak percobaan.')).toBeInTheDocument()
    expect(screen.getByText('Coba lagi dalam 2 menit.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Masuk' })).toBeDisabled()
    expect(screen.getByLabelText('Email')).toHaveValue('admin@contoh.id')
  })

  it('unlocks the button when the wait time is over', async () => {
    stubServer({ login: () => apiError(429, 'too_many_attempts', { 'Retry-After': '2' }) })
    renderApp()
    await fillAndSubmit()
    await screen.findByText('Terlalu banyak percobaan.')
    expect(screen.getByRole('button', { name: 'Masuk' })).toBeDisabled()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Masuk' })).toBeEnabled(), { timeout: 4000 })
  })

  it('keeps the email on a server error', async () => {
    stubServer({ login: () => apiError(500, 'internal_error') })
    renderApp()
    await fillAndSubmit('admin@contoh.id', 'rahasia')

    expect(await screen.findByText('Login belum bisa diproses.')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveValue('admin@contoh.id')
    expect(screen.getByRole('button', { name: 'Masuk' })).toBeEnabled()
  })

  it('keeps the email when the network is down', async () => {
    const server = stubServer()
    renderApp()
    const user = userEvent.setup()
    await user.type(await screen.findByLabelText('Email'), 'admin@contoh.id')
    await user.type(screen.getByLabelText('Password'), 'rahasia')
    vi.mocked(fetch).mockImplementation(async () => {
      throw new TypeError('Failed to fetch')
    })
    await user.click(screen.getByRole('button', { name: 'Masuk' }))
    expect(await screen.findByText('Login belum bisa diproses.')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveValue('admin@contoh.id')
    expect(server.sessionActive).toBe(false)
  })

  it('locks the button and shows progress while the request is pending', async () => {
    let release: (r: Response) => void = () => {}
    stubServer()
    const base = vi.mocked(fetch).getMockImplementation()!
    vi.mocked(fetch).mockImplementation((input, init) =>
      new URL(String(input), 'http://localhost').pathname === '/api/admin/login'
        ? new Promise<Response>((resolve) => { release = resolve })
        : base(input, init),
    )
    renderApp()
    await fillAndSubmit()
    expect(await screen.findByRole('button', { name: /Memproses/ })).toBeDisabled()
    await act(async () => release(apiError(401, 'invalid_credentials')))
    expect(await screen.findByRole('button', { name: 'Masuk' })).toBeEnabled()
    expect(screen.getByText('Email atau password salah.')).toBeInTheDocument()
  })

  it('returns to the page that required admin after login', async () => {
    stubServer()
    renderApp('/admin/booking')
    expect(await screen.findByRole('heading', { name: 'Login Admin' })).toBeInTheDocument()
    await fillAndSubmit()
    expect(await screen.findByRole('heading', { name: 'Booking' })).toBeInTheDocument()
  })

  it('goes straight to the page when a session already exists', async () => {
    stubServer({ sessionActive: true })
    renderApp('/masuk')
    expect(await screen.findByText('Nama Admin')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Login Admin' })).not.toBeInTheDocument()
  })

  it('offers Login Admin to anonymous visitors on public pages', async () => {
    stubServer()
    renderApp('/')
    expect(await screen.findByRole('link', { name: 'Login Admin' })).toHaveAttribute('href', '/masuk')
  })
})

describe('Keluar', () => {
  it('posts logout with the CSRF token, removes the admin header and returns to the dashboard', async () => {
    const server = stubServer()
    renderApp()
    const user = await fillAndSubmit()
    await screen.findByText('Nama Admin')

    await user.click(screen.getByRole('button', { name: 'Keluar' }))
    await waitFor(() => expect(screen.queryByText('Nama Admin')).not.toBeInTheDocument())

    const logout = server.calls.find((c) => c.path === '/api/admin/logout')!
    expect(logout.method).toBe('POST')
    expect(logout.csrf).toBe('csrf-abc')
    expect(screen.queryByRole('link', { name: 'Booking' })).not.toBeInTheDocument()
    expect(await screen.findByRole('link', { name: 'Login Admin' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Login Admin' })).not.toBeInTheDocument()
    expect(server.sessionActive).toBe(false)
  })

  it('ends on the public dashboard when logging out from a guarded admin page', async () => {
    stubServer({ sessionActive: true })
    renderApp('/admin/booking')
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: 'Keluar' }))
    expect(await screen.findByRole('link', { name: 'Login Admin' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Login Admin' })).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Booking' })).not.toBeInTheDocument()
  })

  it('stays in Mode Admin and says so when logout fails', async () => {
    stubServer()
    renderApp()
    const user = await fillAndSubmit()
    await screen.findByText('Nama Admin')
    const base = vi.mocked(fetch).getMockImplementation()!
    vi.mocked(fetch).mockImplementation(async (input, init) =>
      new URL(String(input), 'http://localhost').pathname === '/api/admin/logout' ? apiError(500, 'internal_error') : base(input, init),
    )
    await user.click(screen.getByRole('button', { name: 'Keluar' }))
    expect(await screen.findByText('Belum bisa keluar. Coba lagi.')).toBeInTheDocument()
    expect(screen.getByText('Nama Admin')).toBeInTheDocument()
  })
})

describe('S12 Sesi berakhir', () => {
  it('opens the dialog on a 401 from any admin endpoint, then the login page with a notice', async () => {
    const server = stubServer()
    renderApp()
    const user = await fillAndSubmit()
    await screen.findByText('Nama Admin')

    server.sessionActive = false
    await act(async () => {
      await adminRequest('/api/admin/drivers').catch(() => {})
    })
    const dialog = await screen.findByRole('dialog', { name: 'Sesi berakhir' })
    expect(dialog).toBeInTheDocument()
    expect(screen.queryByText('Nama Admin')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Login ulang' }))
    expect(await screen.findByRole('heading', { name: 'Login Admin' })).toBeInTheDocument()
    expect(screen.getByText('Sesi berakhir, silakan login lagi.')).toBeInTheDocument()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    await user.type(screen.getByLabelText('Email'), 'admin@contoh.id')
    await user.type(screen.getByLabelText('Password'), 'rahasia-benar')
    await user.click(screen.getByRole('button', { name: 'Masuk' }))
    expect(await screen.findByText('Nama Admin')).toBeInTheDocument()
  })

  it('does not open the dialog for a visitor who never logged in', async () => {
    stubServer()
    renderApp('/')
    await screen.findByRole('link', { name: 'Login Admin' })
    await act(async () => {
      await adminRequest('/api/admin/drivers').catch(() => {})
    })
    expect(screen.queryByRole('dialog', { name: 'Sesi berakhir' })).not.toBeInTheDocument()
  })

  it('shows the dialog over an admin page without redirecting before the user acknowledges', async () => {
    const server = stubServer({ sessionActive: true })
    renderApp('/admin/booking')
    await screen.findByRole('heading', { name: 'Booking' })
    server.sessionActive = false
    await act(async () => {
      await adminRequest('/api/admin/bookings').catch(() => {})
    })
    expect(await screen.findByRole('dialog', { name: 'Sesi berakhir' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Login Admin' })).not.toBeInTheDocument()

    await userEvent.setup().click(screen.getByRole('button', { name: 'Login ulang' }))
    expect(await screen.findByRole('heading', { name: 'Login Admin' })).toBeInTheDocument()
    expect(screen.getByText('Sesi berakhir, silakan login lagi.')).toBeInTheDocument()
    server.sessionActive = true
    await fillAndSubmit()
    expect(await screen.findByRole('heading', { name: 'Booking' })).toBeInTheDocument()
  })
})
