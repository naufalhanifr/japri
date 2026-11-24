import { addDays, isIsoDate, MAX_DATE, MIN_DATE, validateRange } from './date'

export type Selection =
  | { kind: 'today' }
  | { kind: 'date'; date: string }
  | { kind: 'range'; start: string; end: string }

export const TODAY: Selection = { kind: 'today' }

export function selectionBounds(selection: Selection, today: string): { start: string; end: string } {
  if (selection.kind === 'today') return { start: today, end: today }
  if (selection.kind === 'date') return { start: selection.date, end: selection.date }
  return { start: selection.start, end: selection.end }
}

export function normalizeSelection(start: string, end: string, today: string): Selection {
  if (start === end) return start === today ? TODAY : { kind: 'date', date: start }
  return { kind: 'range', start, end }
}

export function selectionFromSearch(search: URLSearchParams, today: string): Selection {
  const date = search.get('date')
  const from = search.get('from')
  const to = search.get('to')
  if (from && to && isIsoDate(from) && isIsoDate(to) && validateRange(from, to).ok) {
    return normalizeSelection(from, to, today)
  }
  if (date && isIsoDate(date) && date >= MIN_DATE && date <= MAX_DATE) {
    return normalizeSelection(date, date, today)
  }
  return TODAY
}

export function selectionToSearch(selection: Selection): URLSearchParams {
  const params = new URLSearchParams()
  if (selection.kind === 'date') params.set('date', selection.date)
  if (selection.kind === 'range') {
    params.set('from', selection.start)
    params.set('to', selection.end)
  }
  return params
}

export function selectionKey(selection: Selection): string {
  return selectionToSearch(selection).toString() || 'today'
}

export function shiftSelection(selection: Selection, days: number, today: string): Selection | null {
  if (selection.kind === 'range') return null
  const base = selection.kind === 'today' ? today : selection.date
  const next = addDays(base, days)
  if (next < MIN_DATE || next > MAX_DATE) return null
  return normalizeSelection(next, next, today)
}
