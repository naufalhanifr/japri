import { describe, expect, it } from 'vitest'
import { addDays, formatClock, formatLongDate, inclusiveDays, todayWib, validateRange, wibParts } from './date'

describe('WIB helpers', () => {
  it('reads date and minutes in WIB regardless of the offset in the string', () => {
    expect(wibParts('2026-11-24T23:30:00+07:00')).toEqual({ date: '2026-11-24', minutes: 23 * 60 + 30 })
    expect(wibParts('2026-11-24T20:00:00Z')).toEqual({ date: '2026-11-25', minutes: 3 * 60 })
  })

  it('treats "today" as UTC+7', () => {
    expect(todayWib(new Date('2026-11-24T17:30:00Z'))).toBe('2026-11-25')
    expect(todayWib(new Date('2026-11-24T16:59:00Z'))).toBe('2026-11-24')
  })

  it('formats clock and long dates in Indonesian', () => {
    expect(formatClock('2026-11-24T09:05:00+07:00')).toBe('09:05')
    expect(formatLongDate('2026-11-23')).toBe('Senin, 23 November 2026')
  })

  it('adds days across month boundaries', () => {
    expect(addDays('2026-11-30', 1)).toBe('2026-12-01')
    expect(addDays('2026-03-01', -1)).toBe('2026-02-28')
  })
})

describe('validateRange', () => {
  it('accepts a single day and exactly 31 days', () => {
    expect(validateRange('2026-11-24', '2026-11-24').ok).toBe(true)
    expect(inclusiveDays('2026-11-01', '2026-12-01')).toBe(31)
    expect(validateRange('2026-11-01', '2026-12-01').ok).toBe(true)
  })

  it('rejects 32 days', () => {
    expect(validateRange('2026-11-01', '2026-12-02')).toMatchObject({ ok: false, reason: 'too_long' })
  })

  it('rejects end before start', () => {
    expect(validateRange('2026-11-20', '2026-11-18')).toMatchObject({ ok: false, reason: 'end_before_start' })
  })

  it('rejects empty or malformed input', () => {
    expect(validateRange('', '2026-11-18')).toMatchObject({ ok: false, reason: 'invalid' })
    expect(validateRange('2026-13-40', '2026-11-18')).toMatchObject({ ok: false, reason: 'invalid' })
  })

  it('rejects dates outside 2000-2100', () => {
    expect(validateRange('1999-12-31', '2000-01-02')).toMatchObject({ ok: false, reason: 'out_of_bounds' })
    expect(validateRange('2100-12-30', '2101-01-01')).toMatchObject({ ok: false, reason: 'out_of_bounds' })
    expect(validateRange('2000-01-01', '2000-01-02').ok).toBe(true)
  })
})
