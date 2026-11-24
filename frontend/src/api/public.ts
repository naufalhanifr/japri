import { getJson } from './client'
import type { DashboardData, DriverOption, HistoryPage, OpenBookingsData } from './types'
import type { Selection } from '../lib/selection'

export function selectionParams(selection: Selection): Record<string, string> {
  if (selection.kind === 'date') return { date: selection.date }
  if (selection.kind === 'range') return { from: selection.start, to: selection.end }
  return {}
}

export function fetchDashboard(selection: Selection, signal: AbortSignal): Promise<DashboardData> {
  return getJson<DashboardData>('/api/public/dashboard', selectionParams(selection), signal)
}

export function fetchOpenBookings(driverId: number, signal: AbortSignal): Promise<OpenBookingsData> {
  return getJson<OpenBookingsData>(`/api/public/drivers/${driverId}/open-bookings`, undefined, signal)
}

export interface HistoryQuery {
  driverId: number | null
  from: string | null
  to: string | null
  status: 'selesai' | 'dibatalkan' | null
  page: number
  pageSize: number
}

export function fetchHistory(query: HistoryQuery, signal: AbortSignal): Promise<HistoryPage> {
  const params: Record<string, string> = { page: String(query.page), page_size: String(query.pageSize) }
  if (query.driverId !== null) params.driver_id = String(query.driverId)
  if (query.from) params.from = query.from
  if (query.to) params.to = query.to
  if (query.status) params.status = query.status
  return getJson<HistoryPage>('/api/public/history', params, signal)
}

export function fetchDriverOptions(signal: AbortSignal): Promise<DriverOption[]> {
  return getJson<{ items: DriverOption[] }>('/api/public/drivers', undefined, signal).then((body) => body.items)
}
