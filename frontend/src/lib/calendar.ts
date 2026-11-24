import { addDays, diffDays, isIsoDate, MAX_DATE, MIN_DATE } from './date'

export const WEEKDAYS = [
  { short: 'Sen', long: 'Senin' },
  { short: 'Sel', long: 'Selasa' },
  { short: 'Rab', long: 'Rabu' },
  { short: 'Kam', long: 'Kamis' },
  { short: 'Jum', long: 'Jumat' },
  { short: 'Sab', long: 'Sabtu' },
  { short: 'Min', long: 'Minggu' },
] as const

const MONTHS = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]

export const monthOf = (date: string) => date.slice(0, 7)

export const monthTitle = (month: string) => `${MONTHS[Number(month.slice(5, 7)) - 1]} ${month.slice(0, 4)}`

export function shiftMonth(month: string, delta: number): string {
  const index = Number(month.slice(0, 4)) * 12 + Number(month.slice(5, 7)) - 1 + delta
  return `${Math.floor(index / 12)}-${String((index % 12) + 1).padStart(2, '0')}`
}

export function monthHasDates(month: string): boolean {
  return `${month}-31` >= MIN_DATE && `${month}-01` <= MAX_DATE
}

/** Weeks of the month, Monday first. Cells outside the month are null. */
export function monthWeeks(month: string): (string | null)[][] {
  const first = `${month}-01`
  const lead = (new Date(`${first}T00:00:00Z`).getUTCDay() + 6) % 7
  const cells: (string | null)[] = Array(lead).fill(null)
  for (let day = first; monthOf(day) === month; day = addDays(day, 1)) cells.push(day)
  while (cells.length % 7 !== 0) cells.push(null)
  const weeks: (string | null)[][] = []
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7))
  return weeks
}

export function clampDate(date: string): string {
  if (!isIsoDate(date)) return MIN_DATE
  return date < MIN_DATE ? MIN_DATE : date > MAX_DATE ? MAX_DATE : date
}

export type DayKey = 'ArrowLeft' | 'ArrowRight' | 'ArrowUp' | 'ArrowDown' | 'Home' | 'End' | 'PageUp' | 'PageDown'

export function moveFocus(date: string, key: DayKey): string {
  const weekday = (diffDays('2000-01-03', date) % 7 + 7) % 7
  switch (key) {
    case 'ArrowLeft': return clampDate(addDays(date, -1))
    case 'ArrowRight': return clampDate(addDays(date, 1))
    case 'ArrowUp': return clampDate(addDays(date, -7))
    case 'ArrowDown': return clampDate(addDays(date, 7))
    case 'Home': return clampDate(addDays(date, -weekday))
    case 'End': return clampDate(addDays(date, 6 - weekday))
    case 'PageUp':
    case 'PageDown': {
      const month = shiftMonth(monthOf(date), key === 'PageUp' ? -1 : 1)
      const last = monthWeeks(month).flat().filter(Boolean).length
      return clampDate(`${month}-${String(Math.min(Number(date.slice(8, 10)), last)).padStart(2, '0')}`)
    }
  }
}
