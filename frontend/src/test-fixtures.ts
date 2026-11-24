import type { DashboardData, DriverCardData, PublicBooking, PublicDriver } from './api/types'

export const driver = (id: number, name = `Driver ${id}`): PublicDriver => ({
  id,
  name,
  vehicle_type: 'Toyota Avanza',
  vehicle_plate: `B ${1000 + id} XYZ`,
})

export function booking(overrides: Partial<PublicBooking> & { id: number }): PublicBooking {
  return {
    driver: driver(1),
    requester_name: 'Sari',
    division: 'Keuangan',
    destination: 'Bandara',
    notes: null,
    schedule_type: 'per_jam',
    start_at: '2026-11-24T09:00:00+07:00',
    end_at: '2026-11-24T11:00:00+07:00',
    status: 'terjadwal',
    overdue: false,
    ...overrides,
  }
}

export const card = (id: number, overrides: Partial<DriverCardData> = {}): DriverCardData => ({
  driver: driver(id),
  state: 'standby',
  open_bookings_count: 0,
  current: null,
  running_count: 0,
  next: null,
  ...overrides,
})

export function dashboard(overrides: Partial<DashboardData> = {}): DashboardData {
  return {
    generated_at: '2026-11-24T10:00:00+07:00',
    range: { start_date: '2026-11-24', end_date: '2026-11-24', includes_today: true },
    summary: { running: 1, standby: 1, on_leave: 0, total_trips: 2 },
    drivers: [card(1), card(2)],
    timeline: { start_date: '2026-11-24', end_date: '2026-11-24', items: [] },
    recent_history: [],
    ...overrides,
  }
}
