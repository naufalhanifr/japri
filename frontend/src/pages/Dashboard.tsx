import { useEffect, useMemo, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { DashboardData, DriverCardData, PublicBooking } from '../api/types'
import { Banner } from '../components/Banner'
import { Button } from '../components/Button'
import { DashboardSkeleton } from '../components/DashboardSkeleton'
import { DatePicker } from '../components/DatePicker'
import { DriverCard } from '../components/DriverCard'
import { DriverDetailDialog } from '../components/DriverDetailDialog'
import { Icon } from '../components/Icon'
import { RangeSchedule } from '../components/RangeSchedule'
import { RecentHistory } from '../components/RecentHistory'
import { SummaryCard } from '../components/SummaryCard'
import { Timeline } from '../components/Timeline'
import { useToast } from '../components/Toast'
import { useDashboard } from '../hooks/useDashboard'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatClock, formatLongDate, formatRangeLabel, inclusiveDays, todayWib, wibParts } from '../lib/date'
import { selectionBounds, selectionFromSearch, selectionToSearch, TODAY, type Selection } from '../lib/selection'

export function Dashboard() {
  usePageTitle(null)
  const [search, setSearch] = useSearchParams()
  const selection = useMemo(() => selectionFromSearch(search, todayWib()), [search])
  const { state, retry } = useDashboard(selection)
  const toast = useToast()
  const [opened, setOpened] = useState<{ driverId: number; trigger: HTMLElement | null } | null>(null)

  const data = state.status === 'ready' ? state.data : null
  const today = data ? wibParts(data.generated_at).date : todayWib()
  const { start, end } = selectionBounds(selection, today)
  const isRange = start !== end
  const stale = state.status === 'ready' ? state.stale : null

  const wasStale = useRef(false)
  useEffect(() => {
    if (wasStale.current && state.status === 'ready' && !state.stale) toast('Data kembali diperbarui.')
    wasStale.current = state.status === 'ready' && state.stale !== null
  }, [state, toast])

  const change = (next: Selection) => {
    setOpened(null)
    setSearch(selectionToSearch(next), { replace: false })
  }

  const heading = isRange
    ? `${formatRangeLabel(start, end)} (${inclusiveDays(start, end)} hari)`
    : formatLongDate(start)

  const openDriver = (driverId: number, trigger: HTMLElement | null) => setOpened({ driverId, trigger })
  const closeDriver = () => {
    opened?.trigger?.focus()
    setOpened(null)
  }
  const openedCard = data && opened ? data.drivers.find((c) => c.driver.id === opened.driverId) : undefined

  return (
    <main id="main" className="page" tabIndex={-1}>
      <div className="page__title-row">
        <div>
          <h1 className="page__title">{heading}</h1>
          {data && (
            <p className={`updated${stale ? ' updated--stale' : ''}`}>
              {stale && <Icon name="overdue" size={14} />}
              {stale
                ? `Gagal memperbarui, data per ${formatClock(data.generated_at)}`
                : `Terakhir diperbarui ${formatClock(data.generated_at)}`}
            </p>
          )}
        </div>
        <DatePicker selection={selection} today={today} onChange={change} />
      </div>

      {stale && data && (
        <Banner tone="warning" title="Gagal memperbarui data.">
          Data di bawah masih per {formatClock(data.generated_at)}. Percobaan berikutnya berjalan otomatis.
        </Banner>
      )}

      {state.status === 'loading' && <DashboardSkeleton />}

      {state.status === 'error' && (
        <section className="state-panel" role="alert">
          <h2 className="state-panel__title">
            {state.error.kind === 'rate_limited' ? 'Terlalu banyak permintaan' : 'Dashboard belum bisa dimuat'}
          </h2>
          <p className="state-panel__body">
            {state.error.kind === 'rate_limited'
              ? 'Coba lagi sebentar lagi.'
              : 'Data driver dan jadwal tidak berhasil diambil. Periksa koneksi, lalu coba lagi.'}
          </p>
          <Button variant="primary" onClick={retry}>Coba lagi</Button>
        </section>
      )}

      {data && (
        <DashboardBody
          data={data}
          isRange={isRange}
          start={start}
          end={end}
          today={today}
          onOpen={openDriver}
          onBackToToday={() => change(TODAY)}
        />
      )}

      {data && opened && openedCard && (
        <DriverDetailDialog
          key={opened.driverId}
          driver={openedCard.driver}
          state={openedCard.state}
          today={today}
          onClose={closeDriver}
        />
      )}
    </main>
  )
}

function DashboardBody({
  data,
  isRange,
  start,
  end,
  today,
  onOpen,
  onBackToToday,
}: {
  data: DashboardData
  isRange: boolean
  start: string
  end: string
  today: string
  onOpen: (driverId: number, trigger: HTMLElement | null) => void
  onBackToToday: () => void
}) {
  const live = data.range.includes_today
  const scopeWord = isRange ? 'rentang ini' : 'tanggal ini'
  const bookingsByDriver = useMemo(
    () => new Map(data.timeline.items.map((item) => [item.driver_id, item.bookings])),
    [data.timeline.items],
  )
  const drivers = data.drivers.map((c) => c.driver)
  const driversWithSchedule = data.timeline.items.filter((i) => i.bookings.length > 0).length

  if (!live && data.summary.total_trips === 0) {
    const label = isRange ? formatRangeLabel(start, end) : formatLongDate(start).split(', ')[1]
    return (
      <section className="state-panel">
        <h2 className="state-panel__title">Tidak ada jadwal pada {scopeWord}</h2>
        <p className="state-panel__body">Belum ada booking pada {label}.</p>
        <Button variant="primary" onClick={onBackToToday}>Kembali ke hari ini</Button>
      </section>
    )
  }

  const totalLabel = live && !isRange ? 'Total trip hari ini' : `Total trip pada ${scopeWord}`
  const openCard = (card: DriverCardData, trigger: HTMLElement) => onOpen(card.driver.id, trigger)
  const showDayNotice = !live

  return (
    <>
      {showDayNotice && (
        <Banner tone="info" title={`Anda melihat jadwal ${isRange ? formatRangeLabel(start, end) : formatLongDate(start)}.`}>
          Status Sedang jalan dan Standby hanya ada untuk hari ini.
        </Banner>
      )}

      <dl className="summary-grid">
        {live ? (
          <>
            <SummaryCard label="Sedang jalan" value={data.summary.running ?? 0} tone="running" />
            <SummaryCard label="Standby" value={data.summary.standby ?? 0} tone="standby" />
            <SummaryCard label="Cuti" value={data.summary.on_leave ?? 0} tone="cuti" />
            <SummaryCard label={totalLabel} value={data.summary.total_trips} />
          </>
        ) : (
          <>
            <SummaryCard label={totalLabel} value={data.summary.total_trips} />
            <SummaryCard label="Driver dengan jadwal" value={driversWithSchedule} />
          </>
        )}
      </dl>

      <section aria-labelledby="drivers-title">
        <div className="section-head">
          <h2 id="drivers-title" className="section-head__title">Driver</h2>
          <p className="section-head__count">{data.drivers.length} driver aktif</p>
        </div>
        {data.drivers.length === 0 ? (
          <p className="panel__empty panel__empty--standalone">Driver yang aktif akan tampil di sini setelah admin menambahkannya.</p>
        ) : (
          <ul className="driver-grid">
            {data.drivers.map((card) => (
              <DriverCard
                key={card.driver.id}
                card={card}
                live={live}
                today={today}
                scopeLabel={scopeWord}
                withDate={isRange}
                bookings={bookingsByDriver.get(card.driver.id) ?? ([] as PublicBooking[])}
                onOpen={openCard}
              />
            ))}
          </ul>
        )}
      </section>

      {data.drivers.length === 0 ? (
        <section className="panel" aria-labelledby="timeline-empty-title">
          <h2 id="timeline-empty-title" className="panel__title">Jadwal hari ini</h2>
          <p className="panel__empty">Jadwal muncul setelah ada driver dan booking.</p>
        </section>
      ) : isRange ? (
        <RangeSchedule drivers={drivers} items={data.timeline.items} onOpen={onOpen} />
      ) : (
        <Timeline
          drivers={drivers}
          items={data.timeline.items}
          date={start}
          nowIso={data.generated_at}
          isToday={live}
          onOpen={onOpen}
        />
      )}

      <RecentHistory items={data.recent_history} />
    </>
  )
}
