import { Link } from 'react-router-dom'
import type { PublicBooking } from '../api/types'
import { formatShortDate, wibParts } from '../lib/date'
import { bookingTimeLabel } from '../lib/format'
import { StatusBadge } from './StatusBadge'

export function RecentHistory({ items }: { items: PublicBooking[] }) {
  return (
    <section className="panel" aria-labelledby="history-title">
      <div className="panel__head">
        <h2 id="history-title" className="panel__title">Riwayat terbaru</h2>
        <Link to="/riwayat" className="text-link">Lihat semua riwayat</Link>
      </div>
      {items.length === 0 ? (
        <p className="panel__empty">Booking yang sudah selesai akan muncul di sini.</p>
      ) : (
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
              {items.map((b) => (
                <tr key={b.id}>
                  <td data-label="Tanggal">{formatShortDate(wibParts(b.start_at).date)}</td>
                  <td data-label="Driver">{b.driver.name}</td>
                  <td data-label="Pemesan">
                    <span>
                      {b.requester_name}
                      <span className="history-table__sub">{b.division}</span>
                    </span>
                  </td>
                  <td data-label="Tujuan">{b.destination}</td>
                  <td data-label="Jam">{bookingTimeLabel(b)}</td>
                  <td data-label="Status"><StatusBadge kind={b.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
