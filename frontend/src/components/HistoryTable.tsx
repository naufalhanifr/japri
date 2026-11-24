import type { PublicBooking } from '../api/types'
import { formatShortDate, wibParts } from '../lib/date'
import { bookingTimeLabel } from '../lib/format'
import { StatusBadge } from './StatusBadge'

const SCHEDULE_LABEL = { per_jam: 'Per jam', full_day: 'Sehari penuh' } as const

export function HistoryTable({ items }: { items: PublicBooking[] }) {
  return (
    <div className="table-wrap">
      <table className="history-table">
        <thead>
          <tr>
            <th scope="col">Tanggal</th>
            <th scope="col">Driver</th>
            <th scope="col">Pemesan</th>
            <th scope="col">Tujuan</th>
            <th scope="col">Jam</th>
            <th scope="col">Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((b) => {
            const date = wibParts(b.start_at).date
            return (
              <tr key={b.id} className={b.status === 'dibatalkan' ? 'is-cancelled' : undefined}>
                <td data-label="Tanggal">{formatShortDate(date)} {date.slice(0, 4)}</td>
                <td data-label="Driver">
                  <span>
                    <strong>{b.driver.name}</strong>
                    <span className="history-table__sub">{b.driver.vehicle_type}, {b.driver.vehicle_plate}</span>
                  </span>
                </td>
                <td data-label="Pemesan">
                  <span>
                    {b.requester_name}
                    <span className="history-table__sub">Divisi {b.division}</span>
                  </span>
                </td>
                <td data-label="Tujuan">
                  <span>
                    {b.destination}
                    {b.notes && (
                      <span className="history-table__sub">
                        <strong>Catatan:</strong> {b.notes}
                      </span>
                    )}
                  </span>
                </td>
                <td data-label="Jam">
                  <span>
                    {bookingTimeLabel(b)}
                    <span className="history-table__sub">{SCHEDULE_LABEL[b.schedule_type]}</span>
                  </span>
                </td>
                <td data-label="Status"><StatusBadge kind={b.status} /></td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
