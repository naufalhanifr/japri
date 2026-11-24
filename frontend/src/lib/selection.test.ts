import { describe, expect, it } from 'vitest'
import { normalizeSelection, selectionFromSearch, selectionKey, selectionToSearch, shiftSelection, TODAY } from './selection'

const today = '2026-11-24'
const parse = (q: string) => selectionFromSearch(new URLSearchParams(q), today)

describe('selection', () => {
  it('defaults to today', () => {
    expect(parse('')).toEqual(TODAY)
    expect(parse('date=2026-11-24')).toEqual(TODAY)
  })

  it('reads a single other date and a valid range', () => {
    expect(parse('date=2026-11-23')).toEqual({ kind: 'date', date: '2026-11-23' })
    expect(parse('from=2026-11-20&to=2026-11-26')).toEqual({ kind: 'range', start: '2026-11-20', end: '2026-11-26' })
  })

  it('ignores invalid or over-long ranges and junk dates', () => {
    expect(parse('from=2026-11-26&to=2026-11-20')).toEqual(TODAY)
    expect(parse('from=2026-01-01&to=2026-12-31')).toEqual(TODAY)
    expect(parse('date=besok')).toEqual(TODAY)
    expect(parse('date=1999-01-01')).toEqual(TODAY)
  })

  it('round-trips through the query string', () => {
    const range = normalizeSelection('2026-11-20', '2026-11-26', today)
    expect(selectionToSearch(range).toString()).toBe('from=2026-11-20&to=2026-11-26')
    expect(selectionKey(TODAY)).toBe('today')
  })

  it('shifts single dates by a day and never shifts a range', () => {
    expect(shiftSelection(TODAY, -1, today)).toEqual({ kind: 'date', date: '2026-11-23' })
    expect(shiftSelection({ kind: 'date', date: '2026-11-23' }, 1, today)).toEqual(TODAY)
    expect(shiftSelection({ kind: 'range', start: '2026-11-20', end: '2026-11-26' }, 1, today)).toBeNull()
    expect(shiftSelection({ kind: 'date', date: '2000-01-01' }, -1, today)).toBeNull()
  })
})
