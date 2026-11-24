import { useCallback, useEffect, useState } from 'react'
import { ApiError, isAbortError } from '../api/client'
import { fetchOpenBookings } from '../api/public'
import type { OpenBookingsData } from '../api/types'
import { toApiError } from './useDashboard'

export type OpenBookingsState =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ready'; data: OpenBookingsData }

const LOADING: OpenBookingsState = { status: 'loading' }

export function useOpenBookings(driverId: number, fetcher: typeof fetchOpenBookings = fetchOpenBookings) {
  const [attempt, setAttempt] = useState(0)
  const key = `${driverId}:${attempt}`
  const [raw, setRaw] = useState<{ key: string; value: OpenBookingsState }>({ key, value: LOADING })

  useEffect(() => {
    const controller = new AbortController()
    fetcher(driverId, controller.signal).then(
      (data) => setRaw({ key, value: { status: 'ready', data } }),
      (caught) => {
        if (isAbortError(caught) || controller.signal.aborted) return
        setRaw({ key, value: { status: 'error', error: toApiError(caught) } })
      },
    )
    return () => controller.abort()
  }, [driverId, key, fetcher])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  return { state: raw.key === key ? raw.value : LOADING, retry }
}
