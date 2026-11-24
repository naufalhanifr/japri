import type { PublicBooking } from '../api/types'
import { DEFAULT_HOUR_END, DEFAULT_HOUR_START } from '../config'
import { inclusiveDays, wibParts } from './date'

export interface TimelineBar {
  booking: PublicBooking
  leftPct: number
  widthPct: number
  clippedStart: boolean
  clippedEnd: boolean
  /** "Hari ke-N dari M" for bookings spanning more than one day, else null. */
  dayInfo: { day: number; of: number } | null
}

export interface TimelineRow {
  driverId: number
  lanes: TimelineBar[][]
}

export interface TimelineLayout {
  startHour: number
  endHour: number
  hours: number[]
  rows: TimelineRow[]
  nowPct: number | null
}

interface Clipped {
  booking: PublicBooking
  from: number
  to: number
  clippedStart: boolean
  clippedEnd: boolean
  dayInfo: TimelineBar['dayInfo']
}

const DAY_MINUTES = 24 * 60

function clipToDay(booking: PublicBooking, date: string): Clipped | null {
  const start = wibParts(booking.start_at)
  const end = wibParts(booking.end_at)
  if (end.date < date || start.date > date) return null
  const clippedStart = start.date < date
  const clippedEnd = end.date > date
  const from = clippedStart ? 0 : start.minutes
  const to = clippedEnd ? DAY_MINUTES : end.minutes
  if (to <= from && !clippedStart && !clippedEnd) return null
  const total = inclusiveDays(start.date, end.date)
  const dayInfo = total > 1 ? { day: inclusiveDays(start.date, date), of: total } : null
  return { booking, from, to, clippedStart, clippedEnd, dayInfo }
}

export function hourWindow(clipped: Clipped[]): { startHour: number; endHour: number } {
  let startHour = DEFAULT_HOUR_START
  let endHour = DEFAULT_HOUR_END
  for (const c of clipped) {
    if (!c.clippedStart) startHour = Math.min(startHour, Math.floor(c.from / 60))
    if (!c.clippedEnd) endHour = Math.max(endHour, Math.ceil(c.to / 60))
  }
  return { startHour, endHour }
}

function packLanes(bars: Clipped[]): Clipped[][] {
  const lanes: Clipped[][] = []
  const laneEnds: number[] = []
  const sorted = [...bars].sort((a, b) => a.from - b.from || a.to - b.to)
  for (const bar of sorted) {
    const index = laneEnds.findIndex((end) => end <= bar.from)
    if (index === -1) {
      lanes.push([bar])
      laneEnds.push(bar.to)
    } else {
      lanes[index].push(bar)
      laneEnds[index] = bar.to
    }
  }
  return lanes
}

export function layoutTimeline(
  items: { driver_id: number; bookings: PublicBooking[] }[],
  date: string,
  nowIso: string | null,
): TimelineLayout {
  const perDriver = items.map((item) => ({
    driverId: item.driver_id,
    clipped: item.bookings.flatMap((b) => {
      const c = clipToDay(b, date)
      return c ? [c] : []
    }),
  }))

  const { startHour, endHour } = hourWindow(perDriver.flatMap((d) => d.clipped))
  const windowStart = startHour * 60
  const windowSpan = (endHour - startHour) * 60

  const toBar = (c: Clipped): TimelineBar => {
    const from = Math.max(c.from, windowStart)
    const to = Math.min(c.to, endHour * 60)
    return {
      booking: c.booking,
      leftPct: ((from - windowStart) / windowSpan) * 100,
      widthPct: (Math.max(to - from, 0) / windowSpan) * 100,
      clippedStart: c.clippedStart,
      clippedEnd: c.clippedEnd,
      dayInfo: c.dayInfo,
    }
  }

  let nowPct: number | null = null
  if (nowIso) {
    const now = wibParts(nowIso)
    if (now.date === date && now.minutes >= windowStart && now.minutes <= endHour * 60) {
      nowPct = ((now.minutes - windowStart) / windowSpan) * 100
    }
  }

  return {
    startHour,
    endHour,
    hours: Array.from({ length: endHour - startHour + 1 }, (_, i) => startHour + i),
    rows: perDriver.map((d) => ({
      driverId: d.driverId,
      lanes: packLanes(d.clipped).map((lane) => lane.map(toBar)),
    })),
    nowPct,
  }
}
