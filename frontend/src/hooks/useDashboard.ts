import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ApiError, isAbortError } from '../api/client'
import { fetchDashboard } from '../api/public'
import type { DashboardData } from '../api/types'
import { POLL_INTERVAL_MS } from '../config'
import { createPoller, type Poller } from '../lib/poller'
import { selectionKey, type Selection } from '../lib/selection'

export type DashboardState =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ready'; data: DashboardData; stale: ApiError | null }

const LOADING: DashboardState = { status: 'loading' }

export function toApiError(error: unknown): ApiError {
  return error instanceof ApiError ? error : new ApiError('network', 'Tidak bisa terhubung ke server.')
}

interface Options {
  intervalMs?: number
  fetcher?: typeof fetchDashboard
}

export function useDashboard(selection: Selection, options: Options = {}) {
  const { intervalMs = POLL_INTERVAL_MS, fetcher = fetchDashboard } = options
  const key = selectionKey(selection)
  const [raw, setRaw] = useState<{ key: string; value: DashboardState }>({ key, value: LOADING })
  const pollerRef = useRef<Poller | null>(null)
  const selectionRef = useRef(selection)
  useEffect(() => {
    selectionRef.current = selection
  })

  useEffect(() => {
    const poller = createPoller({
      intervalMs,
      task: async (signal) => {
        try {
          const data = await fetcher(selectionRef.current, signal)
          if (signal.aborted) return
          setRaw({ key, value: { status: 'ready', data, stale: null } })
        } catch (caught) {
          if (isAbortError(caught) || signal.aborted) return
          const error = toApiError(caught)
          setRaw((prev) =>
            prev.key === key && prev.value.status === 'ready'
              ? { key, value: { ...prev.value, stale: error } }
              : { key, value: { status: 'error', error } },
          )
          return error.kind === 'rate_limited' ? (error.retryAfterMs ?? undefined) : undefined
        }
      },
    })
    pollerRef.current = poller
    poller.start()
    return () => {
      poller.stop()
      pollerRef.current = null
    }
  }, [key, intervalMs, fetcher])

  const state = raw.key === key ? raw.value : LOADING

  const retry = useCallback(() => {
    setRaw((prev) => (prev.value.status === 'error' ? { key, value: LOADING } : prev))
    pollerRef.current?.refresh()
  }, [key])

  return useMemo(() => ({ state, retry }), [state, retry])
}
