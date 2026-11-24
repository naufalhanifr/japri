import { useEffect, useId, useRef } from 'react'
import type { DriverState, PublicBooking, PublicDriver } from '../api/types'
import { useOpenBookings } from '../hooks/useOpenBookings'
import { formatLongDate, todayWib, wibParts } from '../lib/date'
import { bookingTimeLabel } from '../lib/format'
import { Avatar } from './Avatar'
import { Button } from './Button'
import { StatusBadge } from './StatusBadge'

interface Props {
  driver: PublicDriver
  state: DriverState | null
  today?: string
  onClose: () => void
}

export function DriverDetailDialog({ driver, state, today = todayWib(), onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)
  const titleId = useId()
  const { state: result, retry } = useOpenBookings(driver.id)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (!dialog.open) dialog.showModal()
    titleRef.current?.focus()
  }, [])

  return (
    <dialog
      ref={dialogRef}
      className="detail"
      aria-labelledby={titleId}
      onClose={onClose}
      onClick={(event) => {
        if (event.target === event.currentTarget) dialogRef.current?.close()
      }}
    >
      <div className="detail__inner">
        <div className="detail__who">
          <Avatar name={driver.name} />
          <div className="detail__who-text">
            <p className="detail__name">{driver.name}</p>
            <p className="detail__vehicle">{driver.vehicle_type} · {driver.vehicle_plate}</p>
          </div>
          {state && <StatusBadge kind={state} />}
        </div>

        <h2 id={titleId} ref={titleRef} tabIndex={-1} className="detail__title">Booking belum selesai</h2>
        <p className="detail__hint">Hanya baca. Urut menurut waktu mulai.</p>

        <div className="detail__content" aria-live="polite" aria-busy={result.status === 'loading'}>
          {result.status === 'loading' && <DetailSkeleton />}
          {result.status === 'error' && (
            <div className="detail__message" role="alert">
              <p className="detail__message-title">
                {result.error.kind === 'not_found'
                  ? 'Driver tidak ditemukan.'
                  : result.error.kind === 'rate_limited'
                    ? 'Terlalu banyak permintaan. Coba lagi sebentar lagi.'
                    : 'Rincian belum bisa dimuat.'}
              </p>
              <p>
                {result.error.kind === 'not_found'
                  ? 'Driver ini mungkin sudah tidak aktif. Tutup rincian ini dan muat ulang dashboard.'
                  : 'Kartu di belakang tetap utuh.'}
              </p>
              {result.error.kind !== 'not_found' && <Button onClick={retry}>Coba lagi</Button>}
            </div>
          )}
          {result.status === 'ready' && (
            result.data.bookings.length === 0 ? (
              <div className="detail__message">
                <p className="detail__message-title">Tidak ada booking yang belum selesai</p>
                <p>
                  {state === 'cuti'
                    ? 'Driver ini sedang cuti dan tidak bisa dipesan.'
                    : 'Driver ini bisa dipesan. Hubungi admin lewat chat untuk memesan.'}
                </p>
              </div>
            ) : (
              <BookingGroups bookings={result.data.bookings} today={today} />
            )
          )}
        </div>

        <div className="detail__actions">
          <Button variant="secondary" onClick={() => dialogRef.current?.close()}>Tutup</Button>
        </div>
      </div>
    </dialog>
  )
}

function BookingGroups({ bookings, today }: { bookings: PublicBooking[]; today: string }) {
  const groups = new Map<string, PublicBooking[]>()
  for (const booking of bookings) {
    const date = wibParts(booking.start_at).date
    groups.set(date, [...(groups.get(date) ?? []), booking])
  }
  return (
    <>
      {[...groups.entries()].map(([date, items]) => (
        <section key={date} className="detail__group">
          <h3 className="detail__group-title">
            {date === today ? `Hari ini · ${formatLongDate(date)}` : formatLongDate(date)}
          </h3>
          <ul className="detail__list">
            {items.map((b) => (
              <li key={b.id} className="detail__item">
                <div className="detail__item-head">
                  <span className="detail__time">{bookingTimeLabel(b)}</span>
                  <StatusBadge kind={b.status} />
                  {b.overdue && <StatusBadge kind="overdue" />}
                </div>
                <p className="detail__destination">{b.destination}</p>
                <p className="detail__line"><span className="detail__key">Pemesan:</span> {b.requester_name} · Divisi {b.division}</p>
                {b.notes && <p className="detail__line"><span className="detail__key">Catatan:</span> {b.notes}</p>}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  )
}

function DetailSkeleton() {
  return (
    <div className="skeleton-stack">
      <span className="skeleton skeleton--line" aria-hidden="true" />
      <span className="skeleton skeleton--block" aria-hidden="true" />
      <span className="skeleton skeleton--block" aria-hidden="true" />
      <span className="visually-hidden">Memuat rincian</span>
    </div>
  )
}
