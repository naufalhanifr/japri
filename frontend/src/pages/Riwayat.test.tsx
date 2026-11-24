import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { DriverOption, HistoryPage } from '../api/types'
import { formatLongDate } from '../lib/date'
import { booking, driver } from '../test-fixtures'
import { Riwayat } from './Riwayat'

const drivers: DriverOption[] = [
  { ...driver(1, 'Budi Santoso'), is_active: true },
  { ...driver(2, 'Slamet Riyadi'), is_active: false },
]

const page = (items: HistoryPage['items'], total = items.length, pageNo = 1): HistoryPage => ({
  items,
  page: pageNo,
  page_size: 20,
  total,
})

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status })

function stubApi(history: (url: URL) => Response | Promise<Response>) {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input), 'http://localhost')
    if (url.pathname === '/api/public/drivers') return json({ items: drivers })
    return history(url)
  })
  vi.stubGlobal('fetch', fn)
  const historyCalls = () =>
    fn.mock.calls.map(([u]) => new URL(String(u), 'http://localhost')).filter((u) => u.pathname === '/api/public/history')
  return { fn, historyCalls }
}

function Where() {
  const { search } = useLocation()
  return <output data-testid="search">{search}</output>
}

function renderAt(url = '/riwayat') {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Riwayat />
      <Where />
    </MemoryRouter>,
  )
}

const day = (date: string) => screen.getByRole('button', { name: formatLongDate(date) })

beforeEach(() => vi.useFakeTimers({ toFake: ['Date'], now: new Date('2026-11-24T03:00:00Z') }))
afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

describe('Riwayat (S3)', () => {
  it('lists finished and cancelled bookings with the public columns and no actions', async () => {
    stubApi(() =>
      json(
        page([
          booking({
            id: 1,
            status: 'selesai',
            requester_name: 'Sari',
            division: 'Keuangan',
            destination: 'Kantor Pajak',
            notes: 'Bawa map dokumen',
            schedule_type: 'per_jam',
          }),
          booking({ id: 2, status: 'dibatalkan', destination: 'Bandara', schedule_type: 'full_day' }),
        ]),
      ),
    )
    renderAt()
    const table = await screen.findByRole('table')
    expect(within(table).getAllByRole('columnheader').map((h) => h.textContent)).toEqual([
      'Tanggal', 'Driver', 'Pemesan', 'Tujuan', 'Jam', 'Status',
    ])
    expect(within(table).getAllByText('Driver 1')).toHaveLength(2)
    expect(within(table).getAllByText('Toyota Avanza, B 1001 XYZ')).toHaveLength(2)
    expect(within(table).getAllByText('Divisi Keuangan')[0]).toBeInTheDocument()
    expect(within(table).getByText('Bawa map dokumen')).toBeInTheDocument()
    expect(within(table).getByText('Per jam')).toBeInTheDocument()
    expect(within(table).getByText('Sehari penuh')).toBeInTheDocument()
    expect(within(table).getByText('Selesai')).toBeInTheDocument()
    expect(within(table).getByText('Dibatalkan')).toBeInTheDocument()
    expect(within(table).queryByRole('button')).not.toBeInTheDocument()
    expect(within(table).queryByRole('link')).not.toBeInTheDocument()
    expect(screen.getByText('Menampilkan 1-2 dari 2 booking')).toBeInTheDocument()
  })

  it('shows a loading state before the first result', async () => {
    stubApi(() => new Promise<Response>(() => {}))
    renderAt()
    expect(await screen.findByText('Memuat riwayat')).toBeInTheDocument()
    expect(screen.getByText('Memuat...')).toBeInTheDocument()
  })

  it('offers inactive drivers in the driver filter', async () => {
    stubApi(() => json(page([])))
    renderAt()
    expect(await screen.findByRole('option', { name: 'Slamet Riyadi (nonaktif)' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Budi Santoso' })).toBeInTheDocument()
  })

  it('combines driver, status and date filters in one request and in the URL', async () => {
    const user = userEvent.setup()
    const { historyCalls } = stubApi(() => json(page([booking({ id: 1, status: 'selesai' })])))
    renderAt()
    await screen.findByRole('table')
    await screen.findByRole('option', { name: 'Budi Santoso' })

    await user.selectOptions(screen.getByLabelText('Driver'), '1')
    await user.selectOptions(screen.getByLabelText('Status'), 'dibatalkan')
    await user.click(screen.getByRole('button', { name: /Tanggal/ }))
    await user.click(screen.getByLabelText('Rentang'))
    await user.click(day('2026-11-10'))
    await user.click(day('2026-11-20'))
    await user.click(screen.getByRole('button', { name: 'Terapkan' }))

    const last = historyCalls().at(-1)!
    expect(Object.fromEntries(last.searchParams)).toEqual({
      driver_id: '1', status: 'dibatalkan', from: '2026-11-10', to: '2026-11-20', page: '1', page_size: '20',
    })
    expect(screen.getByTestId('search')).toHaveTextContent('?driver=1&from=2026-11-10&to=2026-11-20&status=dibatalkan')
    expect(screen.getByRole('button', { name: /Tanggal/ })).toHaveTextContent('10 Nov - 20 Nov 2026')
  })

  it('keeps the filters when moving to the next page and back', async () => {
    const user = userEvent.setup()
    const { historyCalls } = stubApi((url) => {
      const n = Number(url.searchParams.get('page'))
      const items = Array.from({ length: n === 1 ? 20 : 5 }, (_, i) => booking({ id: n * 100 + i }))
      return json(page(items, 25, n))
    })
    renderAt('/riwayat?driver=1&status=selesai')
    expect(await screen.findByText('Menampilkan 1-20 dari 25 booking')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Berikutnya' }))
    expect(await screen.findByText('Menampilkan 21-25 dari 25 booking')).toBeInTheDocument()
    const second = historyCalls().at(-1)!.searchParams
    expect(second.get('page')).toBe('2')
    expect(second.get('driver_id')).toBe('1')
    expect(second.get('status')).toBe('selesai')
    expect(screen.getByRole('button', { name: 'Berikutnya' })).toBeDisabled()
    expect(screen.getByTestId('search')).toHaveTextContent('?driver=1&status=selesai&page=2')
    await user.click(screen.getByRole('button', { name: 'Sebelumnya' }))
    expect(await screen.findByText('Menampilkan 1-20 dari 25 booking')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Sebelumnya' })).toBeDisabled()
  })

  it('goes back to the first page when a filter changes', async () => {
    const user = userEvent.setup()
    const { historyCalls } = stubApi(() => json(page([booking({ id: 1 })], 40)))
    renderAt('/riwayat?page=2')
    await screen.findByRole('table')
    await user.selectOptions(screen.getByLabelText('Status'), 'selesai')
    expect(historyCalls().at(-1)!.searchParams.get('page')).toBe('1')
  })

  it('blocks an end date before the start date in the picker and keeps the results', async () => {
    const user = userEvent.setup()
    const { historyCalls } = stubApi(() => json(page([booking({ id: 1, destination: 'Bandara' })])))
    renderAt()
    await screen.findByText('Bandara')
    const callsBefore = historyCalls().length
    await user.click(screen.getByRole('button', { name: /Tanggal/ }))
    await user.click(screen.getByLabelText('Rentang'))
    await user.click(day('2026-11-20'))
    await user.click(day('2026-11-18'))
    expect(screen.getByText('Tanggal akhir tidak boleh sebelum tanggal mulai.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Terapkan' })).toBeDisabled()
    expect(screen.getByText('Bandara')).toBeInTheDocument()
    expect(historyCalls()).toHaveLength(callsBefore)
  })

  it('shows a clear message for a range over 366 days in the address and does not call the API', async () => {
    const { historyCalls } = stubApi(() => json(page([])))
    renderAt('/riwayat?from=2025-01-01&to=2026-11-24')
    expect(await screen.findByText('Rentang maksimal 366 hari.')).toBeInTheDocument()
    expect(screen.getByText('Perbaiki tanggal di filter untuk melihat hasilnya.')).toBeInTheDocument()
    expect(historyCalls()).toHaveLength(0)
  })

  it('shows a clear message when the address has the end before the start', async () => {
    stubApi(() => json(page([])))
    renderAt('/riwayat?from=2026-11-20&to=2026-11-18')
    expect(await screen.findByText('Tanggal akhir tidak boleh sebelum tanggal mulai.')).toBeInTheDocument()
  })

  it('tells empty history apart from an empty filter result and clears the filters', async () => {
    const user = userEvent.setup()
    stubApi(() => json(page([])))
    const view = renderAt()
    expect(await screen.findByText('Belum ada riwayat')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Hapus filter' })).toBeDisabled()
    view.unmount()

    renderAt('/riwayat?driver=1&status=dibatalkan')
    expect(await screen.findByText('Tidak ada riwayat untuk filter ini')).toBeInTheDocument()
    const clear = screen.getAllByRole('button', { name: 'Hapus filter' })
    expect(clear).toHaveLength(2)
    await user.click(clear[1])
    expect(await screen.findByText('Belum ada riwayat')).toBeInTheDocument()
    expect(screen.getByTestId('search')).toHaveTextContent(/^$/)
  })

  it('clears only the date filter', async () => {
    const user = userEvent.setup()
    stubApi(() => json(page([booking({ id: 1 })])))
    renderAt('/riwayat?driver=1&from=2026-11-10&to=2026-11-20')
    await screen.findByRole('table')
    await user.click(screen.getByRole('button', { name: 'Hapus tanggal' }))
    expect(screen.getByTestId('search')).toHaveTextContent('?driver=1')
    expect(screen.getByRole('button', { name: /Tanggal/ })).toHaveTextContent('Semua tanggal')
  })

  it('keeps the filters and retries after an error', async () => {
    const user = userEvent.setup()
    const { fn } = stubApi(() => json({ error: { code: 'x', message: 'x', details: null } }, 500))
    renderAt('/riwayat?driver=1')
    expect(await screen.findByText('Riwayat belum bisa dimuat')).toBeInTheDocument()
    expect(screen.getByText('Filter Anda tetap tersimpan. Periksa koneksi, lalu coba lagi.')).toBeInTheDocument()
    fn.mockImplementation(async (input: RequestInfo | URL) =>
      String(input).startsWith('/api/public/drivers') ? json({ items: drivers }) : json(page([booking({ id: 1, destination: 'Bandara' })])),
    )
    await user.click(screen.getByRole('button', { name: 'Coba lagi' }))
    expect(await screen.findByText('Bandara')).toBeInTheDocument()
    expect(screen.getByLabelText('Driver')).toHaveValue('1')
  })

  it('explains a driver that no longer exists', async () => {
    stubApi(() => json({ error: { code: 'not_found', message: 'Driver tidak ditemukan.', details: null } }, 404))
    renderAt('/riwayat?driver=99')
    expect(await screen.findByText('Driver tidak ditemukan', { selector: 'h3' })).toBeInTheDocument()
  })

  it('points to the first page when the page is beyond the results', async () => {
    stubApi(() => json(page([], 5, 9)))
    renderAt('/riwayat?page=9')
    expect(await screen.findByText('Halaman ini kosong')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ke halaman pertama' })).toBeInTheDocument()
  })
})
