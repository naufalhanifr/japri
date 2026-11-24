import { useMemo, type CSSProperties } from 'react'
import type { PublicBooking, PublicDriver } from '../api/types'
import { formatClock, formatHour } from '../lib/date'
import { layoutTimeline } from '../lib/timeline'
import { Avatar } from './Avatar'
import { Icon } from './Icon'
import { TimelineBar } from './TimelineBar'

const LANE_HEIGHT = 44

interface Props {
  drivers: PublicDriver[]
  items: { driver_id: number; bookings: PublicBooking[] }[]
  date: string
  /** Server clock; the now-line only shows when this falls on `date`. */
  nowIso: string | null
  isToday: boolean
  onOpen: (driverId: number, trigger: HTMLElement) => void
}

export function Timeline({ drivers, items, date, nowIso, isToday, onOpen }: Props) {
  const layout = useMemo(() => layoutTimeline(items, date, nowIso), [items, date, nowIso])
  const spanHours = layout.endHour - layout.startHour
  const rowById = new Map(layout.rows.map((r) => [r.driverId, r]))
  const style = { '--tl-hours': spanHours } as CSSProperties

  return (
    <section className="panel" aria-labelledby="timeline-title">
      <div className="panel__head">
        <h2 id="timeline-title" className="panel__title">Jadwal {isToday ? 'hari ini' : 'tanggal ini'}</h2>
        <ul className="legend" aria-label="Keterangan warna">
          <li><span className="legend__swatch legend__swatch--berjalan"><Icon name="running" size={12} /></span>Berjalan</li>
          <li><span className="legend__swatch legend__swatch--terjadwal"><Icon name="scheduled" size={12} /></span>Terjadwal</li>
          <li><span className="legend__swatch legend__swatch--selesai"><Icon name="done" size={12} /></span>Selesai</li>
          <li><span className="legend__swatch legend__swatch--overdue"><Icon name="overdue" size={12} /></span>Melewati jam selesai</li>
        </ul>
      </div>
      <p className="panel__hint">Geser ke samping untuk melihat seluruh jam</p>
      <div className="tl-scroll" role="region" aria-label="Jadwal driver per jam" tabIndex={0}>
        <div className="tl" style={style}>
          <div className="tl-row tl-row--axis">
            <div className="tl-label" />
            <div className="tl-track tl-track--axis">
              {layout.hours.map((hour, index) => (
                <span key={hour} className="tl-hour" style={{ left: `${(index / spanHours) * 100}%` }}>
                  {formatHour(hour)}
                </span>
              ))}
              {layout.nowPct !== null && nowIso && (
                <span className="tl-now-label" style={{ left: `${layout.nowPct}%` }}>{formatClock(nowIso)}</span>
              )}
            </div>
          </div>
          {drivers.map((driver) => {
            const row = rowById.get(driver.id)
            const lanes = row?.lanes ?? []
            const empty = lanes.length === 0
            const height = Math.max(1, lanes.length) * LANE_HEIGHT + 8
            return (
              <div key={driver.id} className="tl-row">
                <div className="tl-label">
                  <Avatar name={driver.name} />
                  <span className="tl-label__name">{driver.name}</span>
                </div>
                <div className="tl-track" style={{ height }}>
                  {empty && <span className="tl-empty">Tidak ada jadwal {isToday ? 'hari ini' : 'pada tanggal ini'}</span>}
                  {lanes.map((lane, laneIndex) => (
                    <div key={laneIndex} className="tl-lane" style={{ top: 4 + laneIndex * LANE_HEIGHT, height: LANE_HEIGHT - 4 }}>
                      {lane.map((bar) => (
                        <TimelineBar key={bar.booking.id} bar={bar} nowPct={layout.nowPct} onOpen={onOpen} />
                      ))}
                    </div>
                  ))}
                  {layout.nowPct !== null && <span className="tl-now" aria-hidden="true" style={{ left: `${layout.nowPct}%` }} />}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
