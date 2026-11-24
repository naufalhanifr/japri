import type { CSSProperties } from 'react'
import type { TimelineBar as BarData } from '../lib/timeline'
import { bookingTimeLabel } from '../lib/format'
import { Icon, type IconName } from './Icon'

const STATUS_TEXT = {
  berjalan: 'Berjalan',
  terjadwal: 'Terjadwal',
  selesai: 'Selesai',
  dibatalkan: 'Dibatalkan',
} as const

const STATUS_ICON: Record<keyof typeof STATUS_TEXT, IconName> = {
  berjalan: 'running',
  terjadwal: 'scheduled',
  selesai: 'done',
  dibatalkan: 'cancelled',
}

export function TimelineBar({
  bar,
  nowPct,
  onOpen,
}: {
  bar: BarData
  nowPct: number | null
  onOpen: (driverId: number, trigger: HTMLElement) => void
}) {
  const { booking } = bar
  const status = booking.status
  const timeLabel = bookingTimeLabel(booking)
  const dayText = bar.dayInfo ? `Hari ke-${bar.dayInfo.day} dari ${bar.dayInfo.of}` : null
  const overdueLabel = booking.overdue ? ', melewati jam selesai' : ''
  const accessibleName = [
    `${booking.destination}, ${timeLabel}, ${booking.requester_name}`,
    dayText,
    `${STATUS_TEXT[status]}${overdueLabel}`,
  ].filter(Boolean).join(', ')

  const overrunPct =
    booking.overdue && nowPct !== null ? Math.max(0, nowPct - (bar.leftPct + bar.widthPct)) : 0

  const style: CSSProperties = { left: `${bar.leftPct}%`, width: `${bar.widthPct}%` }
  const classes = [
    'tl-bar',
    `tl-bar--${status}`,
    bar.clippedStart ? 'is-cut-start' : '',
    bar.clippedEnd ? 'is-cut-end' : '',
  ].filter(Boolean).join(' ')

  return (
    <>
      <button
        type="button"
        className={classes}
        style={style}
        aria-haspopup="dialog"
        aria-label={accessibleName}
        title={accessibleName}
        onClick={(event) => onOpen(booking.driver.id, event.currentTarget)}
      >
        <span className="tl-bar__title">
          <Icon name={STATUS_ICON[status]} size={12} />
          <span>{booking.destination}</span>
        </span>
        <span className="tl-bar__meta">
          {dayText ?? `${timeLabel} · ${booking.requester_name}`}
        </span>
      </button>
      {overrunPct > 0 && (
        <span
          className="tl-overrun"
          aria-hidden="true"
          style={{ left: `${bar.leftPct + bar.widthPct}%`, width: `${overrunPct}%` }}
        />
      )}
      {booking.overdue && (
        <span className="tl-flag" aria-hidden="true" style={{ left: `calc(${bar.leftPct + bar.widthPct + overrunPct}% - 10px)` }}>
          <Icon name="overdue" size={14} />
        </span>
      )}
    </>
  )
}
