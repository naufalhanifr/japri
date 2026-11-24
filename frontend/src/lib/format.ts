import type { PublicBooking } from '../api/types'
import { formatClock, formatShortDate, wibParts } from './date'

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  const letters = parts.length > 1 ? parts[0][0] + parts[1][0] : (parts[0] ?? '?').slice(0, 2)
  return letters.toUpperCase()
}

export function bookingTimeLabel(booking: PublicBooking, withDate = false): string {
  const start = wibParts(booking.start_at)
  const end = wibParts(booking.end_at)
  if (start.date === end.date) {
    const clock = `${formatClock(booking.start_at)}-${formatClock(booking.end_at)}`
    return withDate ? `${formatShortDate(start.date)} ${clock}` : clock
  }
  return `${formatShortDate(start.date)} ${formatClock(booking.start_at)} - ${formatShortDate(end.date)} ${formatClock(booking.end_at)}`
}
