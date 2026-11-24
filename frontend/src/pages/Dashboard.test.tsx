import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ToastProvider } from '../components/Toast'
import { booking, card, dashboard, driver } from '../test-fixtures'
import { Dashboard } from './Dashboard'

function stubApi(handler: (url: string) => Response | Promise<Response>) {
  const fn = vi.fn(async (input: RequestInfo | URL) => handler(String(input)))
  vi.stubGlobal('fetch', fn)
  return fn
}
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status })

function renderAt(url = '/') {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <ToastProvider>
        <Dashboard />
      </ToastProvider>
    </MemoryRouter>,
  )
}

afterEach(() => vi.unstubAllGlobals())

describe('Dashboard (S1)', () => {
  it('renders the four numbers, cards, timeline and history for today', async () => {
    const overdue = booking({ id: 1, status: 'berjalan', overdue: true, destination: 'Bandara' })
    stubApi(() =>
      json(
        dashboard({
          summary: { running: 1, standby: 1, on_leave: 0, total_trips: 2 },
          drivers: [card(1, { state: 'sedang_jalan', current: overdue, running_count: 1, open_bookings_count: 1 }), card(2)],
          timeline: { start_date: '2026-11-24', end_date: '2026-11-24', items: [{ driver_id: 1, bookings: [overdue] }, { driver_id: 2, bookings: [] }] },
          recent_history: [booking({ id: 7, status: 'selesai', destination: 'Kantor Pajak' })],
        }),
      ),
    )
    renderAt()
    expect(await screen.findByText('Terakhir diperbarui 10:00')).toBeInTheDocument()
    const summary = screen.getByText('Sedang jalan', { selector: 'dt' }).closest('dl')!
    expect(within(summary).getAllByRole('term').map((t) => t.textContent)).toEqual(['Sedang jalan', 'Standby', 'Cuti', 'Total trip hari ini'])
    expect(screen.getAllByText('Melewati jam selesai').length).toBeGreaterThan(0)
    expect(screen.getByRole('region', { name: 'Jadwal driver per jam' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Lihat semua riwayat' })).toHaveAttribute('href', '/riwayat')
    expect(screen.getByText('Kantor Pajak')).toBeInTheDocument()
  })

  it('shows the error panel on first-load failure and recovers via Coba lagi', async () => {
    const user = userEvent.setup()
    const api = stubApi(() => json({ error: { code: 'x', message: 'x', details: null } }, 500))
    renderAt()
    expect(await screen.findByText('Dashboard belum bisa dimuat')).toBeInTheDocument()
    api.mockImplementation(async () => json(dashboard()))
    await user.click(screen.getByRole('button', { name: 'Coba lagi' }))
    expect(await screen.findByText('Terakhir diperbarui 10:00')).toBeInTheDocument()
  })

  it('shows the 429 copy', async () => {
    stubApi(() => new Response('{}', { status: 429, headers: { 'Retry-After': '30' } }))
    renderAt()
    expect(await screen.findByText('Terlalu banyak permintaan')).toBeInTheDocument()
    expect(screen.getByText('Coba lagi sebentar lagi.')).toBeInTheDocument()
  })

  it('shows the empty-day panel for a date with no trips and a way back to today', async () => {
    stubApi(() =>
      json(
        dashboard({
          range: { start_date: '2026-11-25', end_date: '2026-11-25', includes_today: false },
          summary: { running: null, standby: null, on_leave: null, total_trips: 0 },
          drivers: [card(1, { state: null })],
        }),
      ),
    )
    renderAt('/?date=2026-11-25')
    expect(await screen.findByText('Tidak ada jadwal pada tanggal ini')).toBeInTheDocument()
    expect(screen.getByText('Belum ada booking pada 25 November 2026.')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Kembali ke hari ini' }).length).toBeGreaterThan(0)
  })

  it('shows no live status for another date and uses scope wording', async () => {
    const b = booking({ id: 3, start_at: '2026-11-23T09:00:00+07:00', end_at: '2026-11-23T10:00:00+07:00', status: 'selesai' })
    stubApi(() =>
      json(
        dashboard({
          generated_at: '2026-11-24T10:00:00+07:00',
          range: { start_date: '2026-11-23', end_date: '2026-11-23', includes_today: false },
          summary: { running: null, standby: null, on_leave: null, total_trips: 1 },
          drivers: [card(1, { state: null })],
          timeline: { start_date: '2026-11-23', end_date: '2026-11-23', items: [{ driver_id: 1, bookings: [b] }] },
        }),
      ),
    )
    renderAt('/?date=2026-11-23')
    expect(await screen.findByText('Total trip pada tanggal ini', { selector: 'dt' })).toBeInTheDocument()
    expect(screen.queryByText('Sedang jalan', { selector: 'dt' })).not.toBeInTheDocument()
    expect(screen.queryByText('Standby')).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Senin, 23 November 2026')
  })

  it('shows an empty driver list message (E6)', async () => {
    stubApi(() => json(dashboard({ drivers: [], summary: { running: 0, standby: 0, on_leave: 0, total_trips: 0 } })))
    renderAt()
    expect(await screen.findByText(/Driver yang aktif akan tampil di sini/)).toBeInTheDocument()
  })

  it('opens S2 from a driver card', async () => {
    const user = userEvent.setup()
    const d = driver(1, 'Agus Prasetyo')
    stubApi((url) =>
      url.includes('open-bookings')
        ? json({ driver: d, bookings: [booking({ id: 1, destination: 'Halim' })] })
        : json(dashboard({ drivers: [{ ...card(1), driver: d }] })),
    )
    renderAt()
    await user.click(await screen.findByRole('button', { name: /Agus Prasetyo/ }))
    expect(await screen.findByRole('heading', { name: 'Booking belum selesai' })).toBeInTheDocument()
    expect(await screen.findByText('Halim')).toBeInTheDocument()
  })
})
