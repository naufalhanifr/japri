import { describe, expect, it } from 'vitest'
import { dateFilterLabel, historyToSearch, parseHistorySearch } from './historyQuery'

const parse = (query: string) => parseHistorySearch(new URLSearchParams(query))

describe('historyQuery', () => {
  it('reads valid filters and ignores junk', () => {
    expect(parse('driver=3&status=selesai&from=2026-11-01&to=2026-11-20&page=2')).toEqual({
      driverId: 3, status: 'selesai', from: '2026-11-01', to: '2026-11-20', page: 2, rangeProblem: null,
    })
    expect(parse('driver=abc&status=terjadwal&from=nope&page=-4')).toEqual({
      driverId: null, status: null, from: null, to: null, page: 1, rangeProblem: null,
    })
  })

  it('reports a bad range with the user-facing message', () => {
    expect(parse('from=2026-11-20&to=2026-11-18').rangeProblem).toBe('Tanggal akhir tidak boleh sebelum tanggal mulai.')
    expect(parse('from=2025-01-01&to=2026-11-24').rangeProblem).toBe('Rentang maksimal 366 hari.')
    expect(parse('from=2025-11-23&to=2026-11-24').rangeProblem).toBe('Rentang maksimal 366 hari.')
    expect(parse('from=2025-11-24&to=2026-11-24').rangeProblem).toBeNull()
    expect(parse('from=2025-11-25&to=2026-11-24').rangeProblem).toBeNull()
  })

  it('writes only non-default values', () => {
    const filters = { driverId: 2, from: null, to: null, status: null }
    expect(historyToSearch(filters).toString()).toBe('driver=2')
    expect(historyToSearch(filters, 3).toString()).toBe('driver=2&page=3')
    expect(historyToSearch({ driverId: null, from: null, to: null, status: null }).toString()).toBe('')
  })

  it('labels the date filter', () => {
    expect(dateFilterLabel(null, null)).toBe('Semua tanggal')
    expect(dateFilterLabel('2026-11-10', '2026-11-10')).toBe('10 Nov 2026')
    expect(dateFilterLabel('2026-11-10', '2026-11-20')).toBe('10 Nov - 20 Nov 2026')
  })
})
