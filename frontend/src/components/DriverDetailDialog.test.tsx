import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { booking, driver } from '../test-fixtures'
import { DriverDetailDialog } from './DriverDetailDialog'

function stubFetch(status: number, body: unknown, headers: Record<string, string> = {}) {
  const fn = vi.fn(async () => new Response(JSON.stringify(body), { status, headers }))
  vi.stubGlobal('fetch', fn)
  return fn
}

const d = driver(1, 'Budi Santoso')
const renderDialog = (state: 'standby' | 'cuti' | 'sedang_jalan' | null = 'standby', onClose = vi.fn()) =>
  render(<DriverDetailDialog driver={d} state={state} today="2026-11-24" onClose={onClose} />)

afterEach(() => vi.unstubAllGlobals())

describe('DriverDetailDialog (S2)', () => {
  it('shows loading, then bookings grouped by date with no contact details', async () => {
    stubFetch(200, {
      driver: d,
      bookings: [
        booking({ id: 1, status: 'berjalan', overdue: true, destination: 'Bandara', notes: 'Bawa berkas' }),
        booking({ id: 2, start_at: '2026-11-26T09:00:00+07:00', end_at: '2026-11-26T10:00:00+07:00', destination: 'Bogor' }),
      ],
    })
    renderDialog('sedang_jalan')
    expect(screen.getByText('Memuat rincian')).toBeInTheDocument()
    expect(await screen.findByText('Bandara')).toBeInTheDocument()
    expect(screen.getByText(/Hari ini/)).toBeInTheDocument()
    expect(screen.getByText('Melewati jam selesai')).toBeInTheDocument()
    expect(screen.getByText('Bawa berkas')).toBeInTheDocument()
    expect(screen.getAllByText(/Pemesan:/, { selector: 'span' })).toHaveLength(2)
    expect(screen.getByRole('heading', { name: 'Booking belum selesai' })).toHaveFocus()
    expect(screen.queryByText(/telegram|telepon|whatsapp/i)).not.toBeInTheDocument()
  })

  it('shows the empty state, with Cuti wording when on leave', async () => {
    stubFetch(200, { driver: d, bookings: [] })
    const { unmount } = renderDialog('standby')
    expect(await screen.findByText('Tidak ada booking yang belum selesai')).toBeInTheDocument()
    expect(screen.getByText(/Driver ini bisa dipesan/)).toBeInTheDocument()
    unmount()
    renderDialog('cuti')
    expect(await screen.findByText(/sedang cuti dan tidak bisa dipesan/)).toBeInTheDocument()
  })

  it('shows a retryable error and recovers', async () => {
    const user = userEvent.setup()
    const fn = stubFetch(500, { error: { code: 'internal', message: 'x', details: null } })
    renderDialog()
    expect(await screen.findByText('Rincian belum bisa dimuat.')).toBeInTheDocument()
    fn.mockImplementation(async () => new Response(JSON.stringify({ driver: d, bookings: [booking({ id: 9, destination: 'Cikarang' })] })))
    await user.click(screen.getByRole('button', { name: 'Coba lagi' }))
    expect(await screen.findByText('Cikarang')).toBeInTheDocument()
  })

  it('shows rate-limit and not-found messages (404 has no retry)', async () => {
    stubFetch(429, {}, { 'Retry-After': '10' })
    const { unmount } = renderDialog()
    expect(await screen.findByText(/Terlalu banyak permintaan/)).toBeInTheDocument()
    unmount()
    stubFetch(404, { error: { code: 'not_found', message: 'x', details: null } })
    renderDialog()
    expect(await screen.findByText('Driver tidak ditemukan.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Coba lagi' })).not.toBeInTheDocument()
  })

  it('calls onClose from the Tutup button', async () => {
    const user = userEvent.setup()
    stubFetch(200, { driver: d, bookings: [] })
    const onClose = vi.fn()
    renderDialog('standby', onClose)
    await user.click(screen.getByRole('button', { name: 'Tutup' }, ))
    expect(onClose).toHaveBeenCalled()
  })
})
