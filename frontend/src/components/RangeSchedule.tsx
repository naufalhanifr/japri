import type { PublicBooking, PublicDriver } from '../api/types'
import { formatLongDate, wibParts } from '../lib/date'
import { bookingTimeLabel } from '../lib/format'
import { Avatar } from './Avatar'
import { StatusBadge } from './StatusBadge'

interface Props {
  drivers: PublicDriver[]
  items: { driver_id: number; bookings: PublicBooking[] }[]
  onOpen: (driverId: number, trigger: HTMLElement) => void
}

export function RangeSchedule({ drivers, items, onOpen }: Props) {
  const byId = new Map(drivers.map((d) => [d.id, d]))
  const all = items
    .flatMap((item) => item.bookings)
    .sort((a, b) => a.start_at.localeCompare(b.start_at) || a.id - b.id)

  const groups = new Map<string, PublicBooking[]>()
  for (const booking of all) {
    const date = wibParts(booking.start_at).date
    groups.set(date, [...(groups.get(date) ?? []), booking])
  }

  return (
    <section className="panel" aria-labelledby="range-title">
      <div className="panel__head">
        <h2 id="range-title" className="panel__title">Jadwal pada rentang ini</h2>
      </div>
      {all.length === 0 ? (
        <p className="panel__empty">Tidak ada jadwal pada rentang ini.</p>
      ) : (
        [...groups.entries()].map(([date, bookings]) => (
          <div key={date} className="range-group">
            <h3 className="range-group__title">{formatLongDate(date)}</h3>
            <ul className="range-list">
              {bookings.map((b) => {
                const driver = byId.get(b.driver.id) ?? b.driver
                return (
                  <li key={b.id}>
                    <button type="button" className="range-row" aria-haspopup="dialog" onClick={(e) => onOpen(driver.id, e.currentTarget)}>
                      <Avatar name={driver.name} />
                      <span className="range-row__main">
                        <span className="range-row__title">{driver.name} · {b.destination}</span>
                        <span className="range-row__meta">{bookingTimeLabel(b)} · {b.requester_name}, {b.division}</span>
                      </span>
                      <StatusBadge kind={b.status} />
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        ))
      )}
    </section>
  )
}
