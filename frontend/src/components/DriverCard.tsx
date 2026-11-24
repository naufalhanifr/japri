import type { DriverCardData, PublicBooking } from '../api/types'
import { formatWhen } from '../lib/date'
import { bookingTimeLabel } from '../lib/format'
import { Avatar } from './Avatar'
import { StatusBadge } from './StatusBadge'

interface Props {
  card: DriverCardData
  /** Bookings that fall inside the selected date or range (used when the card is not live). */
  bookings: PublicBooking[]
  live: boolean
  today: string
  scopeLabel: string
  withDate: boolean
  onOpen: (card: DriverCardData, trigger: HTMLElement) => void
}

export function DriverCard({ card, bookings, live, today, scopeLabel, withDate, onOpen }: Props) {
  const { driver } = card
  return (
    <li className="driver-card-item">
      <button
        type="button"
        className="driver-card"
        aria-haspopup="dialog"
        onClick={(event) => onOpen(card, event.currentTarget)}
      >
        <span className="driver-card__head">
          <Avatar name={driver.name} />
          <span className="driver-card__who">
            <span className="driver-card__name">{driver.name}</span>
            <span className="driver-card__vehicle">{driver.vehicle_type} · {driver.vehicle_plate}</span>
          </span>
        </span>
        {live ? <LiveBody card={card} today={today} /> : <ScopeBody bookings={bookings} scopeLabel={scopeLabel} withDate={withDate} />}
        <span className="driver-card__foot">
          {live
            ? `${card.open_bookings_count} booking belum selesai`
            : `${bookings.length} booking pada ${scopeLabel}`}
        </span>
      </button>
    </li>
  )
}

function LiveBody({ card, today }: { card: DriverCardData; today: string }) {
  const { state, current, next, running_count } = card
  const more = (running_count ?? 0) - 1
  return (
    <span className="driver-card__body">
      {state && <span><StatusBadge kind={state} /></span>}
      {state === 'sedang_jalan' && current && (
        <>
          <span className="driver-card__line driver-card__line--strong">{current.destination}</span>
          <span className="driver-card__line">{current.requester_name} · {current.division}</span>
          {current.overdue ? (
            <>
              <span><StatusBadge kind="overdue" /></span>
              <span className="driver-card__line">Seharusnya selesai {formatWhen(current.end_at, today)}</span>
            </>
          ) : (
            <span className="driver-card__line">Selesai {formatWhen(current.end_at, today)}</span>
          )}
          {more > 0 && <span className="driver-card__line driver-card__line--muted">+{more} booking berjalan lainnya</span>}
        </>
      )}
      {state === 'standby' && <span className="driver-card__line driver-card__line--strong">Bisa dipesan sekarang</span>}
      {state === 'cuti' && (
        <>
          <span className="driver-card__line driver-card__line--strong">Sedang cuti</span>
          <span className="driver-card__line">Tidak bisa dipesan selama Cuti</span>
        </>
      )}
      {next ? (
        <span className="driver-card__line">Berikutnya {formatWhen(next.start_at, today)} · {next.destination}</span>
      ) : (
        state !== 'cuti' && <span className="driver-card__line driver-card__line--muted">Tidak ada jadwal berikutnya</span>
      )}
    </span>
  )
}

function ScopeBody({ bookings, scopeLabel, withDate }: { bookings: PublicBooking[]; scopeLabel: string; withDate: boolean }) {
  if (bookings.length === 0) {
    return (
      <span className="driver-card__body">
        <span className="driver-card__line driver-card__line--muted">Tidak ada jadwal pada {scopeLabel}</span>
      </span>
    )
  }
  const shown = bookings.slice(0, 3)
  return (
    <span className="driver-card__body">
      {shown.map((b) => (
        <span key={b.id} className="driver-card__line">
          <span className="driver-card__time">{bookingTimeLabel(b, withDate)}</span>
          {' '}{b.destination} · {b.requester_name}
        </span>
      ))}
      {bookings.length > shown.length && (
        <span className="driver-card__line driver-card__line--muted">+{bookings.length - shown.length} lainnya</span>
      )}
    </span>
  )
}

