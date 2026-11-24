import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client'
import { dashboard } from '../test-fixtures'
import { TODAY } from '../lib/selection'
import { useDashboard } from './useDashboard'

beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())

const flush = () => act(async () => { await vi.advanceTimersByTimeAsync(0) })

describe('useDashboard', () => {
  it('goes loading -> ready', async () => {
    const fetcher = vi.fn().mockResolvedValue(dashboard())
    const { result } = renderHook(() => useDashboard(TODAY, { intervalMs: 30_000, fetcher }))
    expect(result.current.state.status).toBe('loading')
    await flush()
    expect(result.current.state).toMatchObject({ status: 'ready', stale: null })
  })

  it('shows an error when the first load fails, and retry recovers', async () => {
    const fetcher = vi.fn().mockRejectedValueOnce(new ApiError('server', 'x', { status: 500 })).mockResolvedValue(dashboard())
    const { result } = renderHook(() => useDashboard(TODAY, { intervalMs: 30_000, fetcher }))
    await flush()
    expect(result.current.state).toMatchObject({ status: 'error', error: { kind: 'server' } })
    act(() => result.current.retry())
    expect(result.current.state.status).toBe('loading')
    await flush()
    expect(result.current.state.status).toBe('ready')
  })

  it('keeps old data and marks it stale when a refresh fails, then clears on success', async () => {
    const first = dashboard({ generated_at: '2026-11-24T10:00:00+07:00' })
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(first)
      .mockRejectedValueOnce(new ApiError('network', 'offline'))
      .mockResolvedValue(dashboard({ generated_at: '2026-11-24T10:01:00+07:00' }))
    const { result } = renderHook(() => useDashboard(TODAY, { intervalMs: 30_000, fetcher }))
    await flush()
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000) })
    const stale = result.current.state
    expect(stale).toMatchObject({ status: 'ready', stale: { kind: 'network' } })
    expect(stale.status === 'ready' && stale.data).toBe(first)
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000) })
    expect(result.current.state).toMatchObject({ status: 'ready', stale: null })
  })

  it('shows a rate-limit error and honours Retry-After before the next try', async () => {
    const fetcher = vi
      .fn()
      .mockRejectedValueOnce(new ApiError('rate_limited', 'x', { status: 429, retryAfterMs: 90_000 }))
      .mockResolvedValue(dashboard())
    const { result } = renderHook(() => useDashboard(TODAY, { intervalMs: 30_000, fetcher }))
    await flush()
    expect(result.current.state).toMatchObject({ status: 'error', error: { kind: 'rate_limited' } })
    await act(async () => { await vi.advanceTimersByTimeAsync(60_000) })
    expect(fetcher).toHaveBeenCalledTimes(1)
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000) })
    expect(fetcher).toHaveBeenCalledTimes(2)
  })

  it('goes back to loading when the selection changes and never shows the old date', async () => {
    const fetcher = vi.fn().mockResolvedValue(dashboard())
    const { result, rerender } = renderHook(({ sel }) => useDashboard(sel, { intervalMs: 30_000, fetcher }), {
      initialProps: { sel: TODAY as Parameters<typeof useDashboard>[0] },
    })
    await flush()
    expect(result.current.state.status).toBe('ready')
    rerender({ sel: { kind: 'date', date: '2026-11-23' } })
    expect(result.current.state.status).toBe('loading')
    await flush()
    expect(fetcher).toHaveBeenLastCalledWith({ kind: 'date', date: '2026-11-23' }, expect.any(AbortSignal))
  })
})
