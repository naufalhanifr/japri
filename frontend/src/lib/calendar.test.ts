import { describe, expect, it } from 'vitest'
import { clampDate, monthHasDates, monthTitle, monthWeeks, moveFocus, shiftMonth } from './calendar'

describe('calendar', () => {
  it('lays out November 2026 Monday first with null padding', () => {
    const weeks = monthWeeks('2026-11')
    expect(weeks).toHaveLength(6)
    expect(weeks[0]).toEqual([null, null, null, null, null, null, '2026-11-01'])
    expect(weeks[1][0]).toBe('2026-11-02')
    expect(weeks[5]).toEqual(['2026-11-30', null, null, null, null, null, null])
    expect(monthWeeks('2026-10')[0].slice(0, 3)).toEqual([null, null, null])
    expect(monthWeeks('2026-10')[0][3]).toBe('2026-10-01')
  })

  it('shifts months across a year boundary', () => {
    expect(shiftMonth('2026-12', 1)).toBe('2027-01')
    expect(shiftMonth('2027-01', -1)).toBe('2026-12')
    expect(monthTitle('2026-11')).toBe('November 2026')
  })

  it('stops at the supported date window', () => {
    expect(monthHasDates('1999-12')).toBe(false)
    expect(monthHasDates('2000-01')).toBe(true)
    expect(clampDate('1990-01-01')).toBe('2000-01-01')
    expect(moveFocus('2000-01-01', 'ArrowLeft')).toBe('2000-01-01')
  })

  it('moves focus like a date grid', () => {
    expect(moveFocus('2026-11-24', 'ArrowRight')).toBe('2026-11-25')
    expect(moveFocus('2026-11-24', 'ArrowUp')).toBe('2026-11-17')
    expect(moveFocus('2026-11-24', 'Home')).toBe('2026-11-23')
    expect(moveFocus('2026-11-24', 'End')).toBe('2026-11-29')
    expect(moveFocus('2026-01-31', 'PageDown')).toBe('2026-02-28')
    expect(moveFocus('2026-03-31', 'PageUp')).toBe('2026-02-28')
  })
})
