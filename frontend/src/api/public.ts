import { getJson } from './client'
import type { DashboardData, OpenBookingsData } from './types'
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
