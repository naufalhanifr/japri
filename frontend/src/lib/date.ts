import { MAX_RANGE_DAYS } from '../config'

const WIB_OFFSET_MS = 7 * 60 * 60 * 1000
const DAY_MS = 24 * 60 * 60 * 1000

export const MIN_DATE = '2000-01-01'
export const MAX_DATE = '2100-12-31'

const DAY_NAMES = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
const MONTH_NAMES = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]

const pad = (n: number) => String(n).padStart(2, '0')

function toUtcMs(date: string): number {
  const [y, m, d] = date.split('-').map(Number)
  return Date.UTC(y, m - 1, d)
}

function fromUtcMs(ms: number): string {
  const d = new Date(ms)
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`
}

export function isIsoDate(value: string | null | undefined): value is string {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  return fromUtcMs(toUtcMs(value)) === value
}

export function todayWib(now: Date = new Date()): string {
  return fromUtcMs(now.getTime() + WIB_OFFSET_MS)
}

export function addDays(date: string, days: number): string {
  return fromUtcMs(toUtcMs(date) + days * DAY_MS)
}

export function diffDays(from: string, to: string): number {
  return Math.round((toUtcMs(to) - toUtcMs(from)) / DAY_MS)
}

export function inclusiveDays(start: string, end: string): number {
  return diffDays(start, end) + 1
}

export function wibParts(iso: string): { date: string; minutes: number } {
  const shifted = new Date(new Date(iso).getTime() + WIB_OFFSET_MS)
  return {
    date: fromUtcMs(shifted.getTime()),
    minutes: shifted.getUTCHours() * 60 + shifted.getUTCMinutes(),
  }
}

export function formatClock(iso: string): string {
  const { minutes } = wibParts(iso)
  return `${pad(Math.floor(minutes / 60))}:${pad(minutes % 60)}`
}

export function formatHour(hour: number): string {
  return `${pad(hour)}:00`
}

export function formatLongDate(date: string): string {
  const d = new Date(toUtcMs(date))
  return `${DAY_NAMES[d.getUTCDay()]}, ${d.getUTCDate()} ${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCFullYear()}`
}

export function formatDayMonth(date: string): string {
  const d = new Date(toUtcMs(date))
  return `${d.getUTCDate()} ${MONTH_NAMES[d.getUTCMonth()]}`
}

export function formatShortDate(date: string): string {
  const d = new Date(toUtcMs(date))
  return `${d.getUTCDate()} ${MONTH_NAMES[d.getUTCMonth()].slice(0, 3)}`
}

export function formatRangeLabel(start: string, end: string): string {
  const sameYear = start.slice(0, 4) === end.slice(0, 4)
  const startLabel = sameYear ? formatShortDate(start) : `${formatShortDate(start)} ${start.slice(0, 4)}`
  return `${startLabel} - ${formatShortDate(end)} ${end.slice(0, 4)}`
}

export function formatWhen(iso: string, today: string): string {
  const { date } = wibParts(iso)
  return date === today ? formatClock(iso) : `${formatShortDate(date)} ${formatClock(iso)}`
}

export type RangeProblem = 'invalid' | 'out_of_bounds' | 'end_before_start' | 'too_long'

export type RangeCheck = { ok: true } | { ok: false; reason: RangeProblem; message: string }

export function validateRange(start: string, end: string, maxDays: number = MAX_RANGE_DAYS): RangeCheck {
  if (!isIsoDate(start) || !isIsoDate(end)) {
    return { ok: false, reason: 'invalid', message: 'Isi tanggal mulai dan tanggal akhir.' }
  }
  if (start < MIN_DATE || end > MAX_DATE || end < MIN_DATE || start > MAX_DATE) {
    return {
      ok: false,
      reason: 'out_of_bounds',
      message: `Tanggal harus antara ${formatShortDate(MIN_DATE)} ${MIN_DATE.slice(0, 4)} dan ${formatShortDate(MAX_DATE)} ${MAX_DATE.slice(0, 4)}.`,
    }
  }
  if (end < start) {
    return { ok: false, reason: 'end_before_start', message: 'Tanggal akhir tidak boleh sebelum tanggal mulai.' }
  }
  if (inclusiveDays(start, end) > maxDays) {
    return { ok: false, reason: 'too_long', message: `Rentang maksimal ${maxDays} hari.` }
  }
  return { ok: true }
}
