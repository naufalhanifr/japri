import { HISTORY_MAX_RANGE_DAYS } from '../config'
import { formatRangeLabel, formatShortDate, isIsoDate, MAX_DATE, MIN_DATE, validateRange } from './date'

export type HistoryStatus = 'selesai' | 'dibatalkan'

export interface HistoryFilters {
  driverId: number | null
  from: string | null
  to: string | null
  status: HistoryStatus | null
}

export interface HistoryParams extends HistoryFilters {
  page: number
  rangeProblem: string | null
}

const inBounds = (date: string | null): date is string =>
  date !== null && isIsoDate(date) && date >= MIN_DATE && date <= MAX_DATE

export function parseHistorySearch(search: URLSearchParams): HistoryParams {
  const rawDriver = Number(search.get('driver'))
  const rawStatus = search.get('status')
  const rawPage = Number(search.get('page'))
  const from = inBounds(search.get('from')) ? search.get('from') : null
  const to = inBounds(search.get('to')) ? search.get('to') : null
  const check = from && to ? validateRange(from, to, HISTORY_MAX_RANGE_DAYS) : null
  return {
    driverId: Number.isInteger(rawDriver) && rawDriver > 0 ? rawDriver : null,
    from,
    to,
    status: rawStatus === 'selesai' || rawStatus === 'dibatalkan' ? rawStatus : null,
    page: Number.isInteger(rawPage) && rawPage > 1 ? rawPage : 1,
    rangeProblem: check && !check.ok ? check.message : null,
  }
}

export function historyToSearch(filters: HistoryFilters, page = 1): URLSearchParams {
  const params = new URLSearchParams()
  if (filters.driverId !== null) params.set('driver', String(filters.driverId))
  if (filters.from) params.set('from', filters.from)
  if (filters.to) params.set('to', filters.to)
  if (filters.status) params.set('status', filters.status)
  if (page > 1) params.set('page', String(page))
  return params
}

export const hasFilters = (filters: HistoryFilters) =>
  filters.driverId !== null || filters.from !== null || filters.to !== null || filters.status !== null

export function dateFilterLabel(from: string | null, to: string | null): string {
  if (from && to) {
    return from === to ? `${formatShortDate(from)} ${from.slice(0, 4)}` : formatRangeLabel(from, to)
  }
  if (from) return `Mulai ${formatShortDate(from)} ${from.slice(0, 4)}`
  if (to) return `Sampai ${formatShortDate(to)} ${to.slice(0, 4)}`
  return 'Semua tanggal'
}
