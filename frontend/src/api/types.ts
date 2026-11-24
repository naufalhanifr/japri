export interface PublicDriver {
  id: number
  name: string
  vehicle_type: string
  vehicle_plate: string
}

export type BookingStatus = 'terjadwal' | 'berjalan' | 'selesai' | 'dibatalkan'
export type DriverState = 'sedang_jalan' | 'standby' | 'cuti'

export interface PublicBooking {
  id: number
  driver: PublicDriver
  requester_name: string
  division: string
  destination: string
  notes: string | null
  schedule_type: 'per_jam' | 'full_day'
  start_at: string
  end_at: string
  status: BookingStatus
  overdue: boolean
}

export interface DriverCardData {
  driver: PublicDriver
  state: DriverState | null
  open_bookings_count: number
  current: PublicBooking | null
  running_count: number | null
  next: PublicBooking | null
}

export interface DashboardData {
  generated_at: string
  range: { start_date: string; end_date: string; includes_today: boolean }
  summary: {
    running: number | null
    standby: number | null
    on_leave: number | null
    total_trips: number
  }
  drivers: DriverCardData[]
  timeline: {
    start_date: string
    end_date: string
    items: { driver_id: number; bookings: PublicBooking[] }[]
  }
  recent_history: PublicBooking[]
}

export interface OpenBookingsData {
  driver: PublicDriver
  bookings: PublicBooking[]
}

export interface DriverOption extends PublicDriver {
  is_active: boolean
}

export interface HistoryPage {
  items: PublicBooking[]
  page: number
  page_size: number
  total: number
}

export interface AdminProfile {
  id: number
  email: string
  display_name: string
}
