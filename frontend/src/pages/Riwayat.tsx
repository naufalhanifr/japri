import { useMemo, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { HistoryPage } from '../api/types'
import { HISTORY_PAGE_SIZE } from '../config'
import { Button } from '../components/Button'
import { HistoryFilters } from '../components/HistoryFilters'
import { HistoryTable } from '../components/HistoryTable'
import { Icon } from '../components/Icon'
import { useDriverOptions, useHistory } from '../hooks/useHistory'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatShortDate, todayWib } from '../lib/date'
import {
  hasFilters,
  historyToSearch,
  parseHistorySearch,
  type HistoryFilters as Filters,
} from '../lib/historyQuery'

export function Riwayat() {
  usePageTitle('Riwayat')
  const [search, setSearch] = useSearchParams()
  const params = useMemo(() => parseHistorySearch(search), [search])
  const filters: Filters = {
    driverId: params.driverId,
    from: params.from,
    to: params.to,
    status: params.status,
  }
  const drivers = useDriverOptions()
  const query = params.rangeProblem
    ? null
    : { ...filters, page: params.page, pageSize: HISTORY_PAGE_SIZE }
  const { state, retry } = useHistory(query)
  const resultsRef = useRef<HTMLElement>(null)

  const go = (next: Filters, page = 1) => setSearch(historyToSearch(next, page))
  const reset = () => go({ driverId: null, from: null, to: null, status: null })
  const goToPage = (page: number) => {
    go(filters, page)
    resultsRef.current?.focus()
  }

  const filtered = hasFilters(filters)
  const driverName =
    filters.driverId !== null && drivers.state.status === 'ready'
      ? drivers.state.drivers.find((d) => d.id === filters.driverId)?.name
      : undefined

  return (
    <main id="main" className="page" tabIndex={-1}>
      <div>
        <h1 className="page__title">Riwayat booking</h1>
        <p className="page__lead">
          Booking yang sudah Selesai atau Dibatalkan. Booking yang masih berjalan atau terjadwal ada di Dashboard.
        </p>
      </div>

      <HistoryFilters
        filters={filters}
        drivers={drivers.state}
        today={todayWib()}
        rangeProblem={params.rangeProblem}
        onChange={(next) => go(next)}
        onReset={reset}
        onRetryDrivers={drivers.retry}
      />

      <section className="panel" ref={resultsRef} tabIndex={-1} aria-labelledby="results-title" aria-busy={state.status === 'loading'}>
        <div className="panel__head">
          <h2 id="results-title" className="panel__title">{driverName ?? 'Semua driver'}</h2>
          <p className="panel__hint">
            {state.status === 'loading' && !params.rangeProblem && 'Memuat...'}
            {state.status === 'ready' && summaryLine(filters, state.data.total)}
          </p>
        </div>

        {params.rangeProblem && (
          <p className="panel__empty">Perbaiki tanggal di filter untuk melihat hasilnya.</p>
        )}

        {!params.rangeProblem && state.status === 'loading' && <HistorySkeleton />}

        {!params.rangeProblem && state.status === 'error' && (
          <div className="state-block" role="alert">
            <Icon name="overdue" size={24} />
            {state.error.kind === 'not_found' ? (
              <>
                <h3 className="state-block__title">Driver tidak ditemukan</h3>
                <p className="state-block__body">Driver di filter ini tidak ada. Hapus filter untuk melihat semua riwayat.</p>
                <Button variant="primary" onClick={reset}>Hapus filter</Button>
              </>
            ) : (
              <>
                <h3 className="state-block__title">
                  {state.error.kind === 'rate_limited' ? 'Terlalu banyak permintaan' : 'Riwayat belum bisa dimuat'}
                </h3>
                <p className="state-block__body">
                  {state.error.kind === 'rate_limited'
                    ? 'Tunggu sebentar, lalu coba lagi. Filter Anda tetap tersimpan.'
                    : 'Filter Anda tetap tersimpan. Periksa koneksi, lalu coba lagi.'}
                </p>
                <Button variant="primary" onClick={retry}>Coba lagi</Button>
              </>
            )}
          </div>
        )}

        {!params.rangeProblem && state.status === 'ready' && (
          <ResultBody
            data={state.data}
            filtered={filtered}
            onReset={reset}
            onPage={goToPage}
          />
        )}
      </section>
    </main>
  )
}

function summaryLine(filters: Filters, total: number): string {
  if (total === 0) return ''
  const count = `${total} booking`
  if (!filters.from || !filters.to) return `${count} · terbaru di atas`
  const range =
    filters.from === filters.to
      ? `${formatShortDate(filters.from)} ${filters.from.slice(0, 4)}`
      : `${formatShortDate(filters.from)} sampai ${formatShortDate(filters.to)} ${filters.to.slice(0, 4)}`
  return `${range} · ${count}`
}

function ResultBody({
  data,
  filtered,
  onReset,
  onPage,
}: {
  data: HistoryPage
  filtered: boolean
  onReset: () => void
  onPage: (page: number) => void
}) {
  if (data.total === 0) {
    return filtered ? (
      <div className="state-block">
        <Icon name="info" size={24} />
        <h3 className="state-block__title">Tidak ada riwayat untuk filter ini</h3>
        <p className="state-block__body">Coba ubah tanggal atau status, atau hapus semua filter.</p>
        <Button variant="primary" onClick={onReset}>Hapus filter</Button>
      </div>
    ) : (
      <div className="state-block">
        <Icon name="info" size={24} />
        <h3 className="state-block__title">Belum ada riwayat</h3>
        <p className="state-block__body">Booking yang sudah selesai atau dibatalkan akan muncul di sini.</p>
      </div>
    )
  }

  if (data.items.length === 0) {
    return (
      <div className="state-block">
        <Icon name="info" size={24} />
        <h3 className="state-block__title">Halaman ini kosong</h3>
        <p className="state-block__body">Hasil hanya sampai halaman {Math.ceil(data.total / data.page_size)}.</p>
        <Button variant="primary" onClick={() => onPage(1)}>Ke halaman pertama</Button>
      </div>
    )
  }

  const first = (data.page - 1) * data.page_size + 1
  const last = first + data.items.length - 1
  return (
    <>
      <HistoryTable items={data.items} />
      <nav className="pager" aria-label="Halaman riwayat">
        <p className="pager__info">Menampilkan {first}-{last} dari {data.total} booking</p>
        <div className="pager__buttons">
          <Button variant="secondary" disabled={data.page <= 1} onClick={() => onPage(data.page - 1)}>
            <Icon name="prev" size={16} />
            Sebelumnya
          </Button>
          <Button variant="secondary" disabled={last >= data.total} onClick={() => onPage(data.page + 1)}>
            Berikutnya
            <Icon name="next" size={16} />
          </Button>
        </div>
      </nav>
    </>
  )
}

function HistorySkeleton() {
  return (
    <div className="skeleton-stack">
      <span className="visually-hidden" role="status">Memuat riwayat</span>
      {Array.from({ length: 5 }, (_, i) => (
        <span key={i} className="skeleton skeleton--block" aria-hidden="true" />
      ))}
    </div>
  )
}
