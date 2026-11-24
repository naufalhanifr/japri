import { useCallback, useEffect, useMemo, useState } from 'react'
import { ApiError, isAbortError } from '../api/client'
import { fetchDriverOptions, fetchHistory, type HistoryQuery } from '../api/public'
import type { DriverOption, HistoryPage } from '../api/types'
import { toApiError } from './useDashboard'

export type HistoryState =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ready'; data: HistoryPage }

const LOADING: HistoryState = { status: 'loading' }

export function useHistory(query: HistoryQuery | null, fetcher: typeof fetchHistory = fetchHistory) {
  const [attempt, setAttempt] = useState(0)
  const { driverId = null, from = null, to = null, status = null, page = 1, pageSize = 20 } = query ?? {}
  const enabled = query !== null
  const key = [enabled, driverId, from, to, status, page, pageSize, attempt].join('|')
  const [raw, setRaw] = useState<{ key: string; value: HistoryState }>({ key, value: LOADING })

  useEffect(() => {
    if (!enabled) return
    const controller = new AbortController()
    fetcher({ driverId, from, to, status, page, pageSize }, controller.signal).then(
      (data) => setRaw({ key, value: { status: 'ready', data } }),
      (caught) => {
        if (isAbortError(caught) || controller.signal.aborted) return
        setRaw({ key, value: { status: 'error', error: toApiError(caught) } })
      },
    )
    return () => controller.abort()
  }, [enabled, driverId, from, to, status, page, pageSize, key, fetcher])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  const state = raw.key === key ? raw.value : LOADING
  return useMemo(() => ({ state, retry }), [state, retry])
}

export type DriverOptionsState =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ready'; drivers: DriverOption[] }

export function useDriverOptions(fetcher: typeof fetchDriverOptions = fetchDriverOptions) {
  const [attempt, setAttempt] = useState(0)
  const [raw, setRaw] = useState<{ attempt: number; value: DriverOptionsState }>({ attempt, value: { status: 'loading' } })

  useEffect(() => {
    const controller = new AbortController()
    fetcher(controller.signal).then(
      (drivers) => setRaw({ attempt, value: { status: 'ready', drivers } }),
      (caught) => {
        if (isAbortError(caught) || controller.signal.aborted) return
        setRaw({ attempt, value: { status: 'error', error: toApiError(caught) } })
      },
    )
    return () => controller.abort()
  }, [attempt, fetcher])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  const state: DriverOptionsState = raw.attempt === attempt ? raw.value : { status: 'loading' }
  return { state, retry }
}
