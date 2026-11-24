import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPoller } from './poller'

function setup(task: (signal: AbortSignal) => Promise<number | void> = vi.fn(async () => {})) {
  let hidden = false
  const target = new EventTarget()
  const setHidden = (value: boolean) => {
    hidden = value
    target.dispatchEvent(new Event('visibilitychange'))
  }
  const poller = createPoller({
    task,
    intervalMs: 30_000,
    isHidden: () => hidden,
    target: target as unknown as Document,
  })
  return { poller, task, setHidden }
}

beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())

describe('createPoller', () => {
  it('runs at once, then every interval', async () => {
    const { poller, task } = setup()
    poller.start()
    await vi.advanceTimersByTimeAsync(0)
    expect(task).toHaveBeenCalledTimes(1)
    await vi.advanceTimersByTimeAsync(29_999)
    expect(task).toHaveBeenCalledTimes(1)
    await vi.advanceTimersByTimeAsync(1)
    expect(task).toHaveBeenCalledTimes(2)
    poller.stop()
  })

  it('stops while hidden and fires exactly one request on return', async () => {
    const { poller, task, setHidden } = setup()
    poller.start()
    await vi.advanceTimersByTimeAsync(0)
    setHidden(true)
    await vi.advanceTimersByTimeAsync(120_000)
    expect(task).toHaveBeenCalledTimes(1)
    setHidden(false)
    await vi.advanceTimersByTimeAsync(0)
    expect(task).toHaveBeenCalledTimes(2)
    await vi.advanceTimersByTimeAsync(30_000)
    expect(task).toHaveBeenCalledTimes(3)
    poller.stop()
  })

  it('does not start a request when started in a hidden tab', async () => {
    const { poller, task, setHidden } = setup()
    setHidden(true)
    poller.start()
    await vi.advanceTimersByTimeAsync(60_000)
    expect(task).not.toHaveBeenCalled()
    setHidden(false)
    await vi.advanceTimersByTimeAsync(0)
    expect(task).toHaveBeenCalledTimes(1)
    poller.stop()
  })

  it('aborts the in-flight request when the tab is hidden', async () => {
    let signal: AbortSignal | undefined
    const task = vi.fn((s: AbortSignal) => {
      signal = s
      return new Promise<void>(() => {})
    })
    const { poller, setHidden } = setup(task)
    poller.start()
    await vi.advanceTimersByTimeAsync(0)
    expect(signal?.aborted).toBe(false)
    setHidden(true)
    expect(signal?.aborted).toBe(true)
    poller.stop()
  })

  it('keeps polling after a failing task', async () => {
    const task = vi.fn().mockRejectedValueOnce(new Error('boom')).mockResolvedValue(undefined)
    const { poller } = setup(task)
    poller.start()
    await vi.advanceTimersByTimeAsync(0)
    await vi.advanceTimersByTimeAsync(30_000)
    expect(task).toHaveBeenCalledTimes(2)
    poller.stop()
  })

  it('waits for the longer delay the task asks for (Retry-After)', async () => {
    const task = vi.fn().mockResolvedValueOnce(90_000).mockResolvedValue(undefined)
    const { poller } = setup(task)
    poller.start()
    await vi.advanceTimersByTimeAsync(0)
    await vi.advanceTimersByTimeAsync(60_000)
    expect(task).toHaveBeenCalledTimes(1)
    await vi.advanceTimersByTimeAsync(30_000)
    expect(task).toHaveBeenCalledTimes(2)
    poller.stop()
  })

  it('never runs after stop', async () => {
    const { poller, task } = setup()
    poller.start()
    await vi.advanceTimersByTimeAsync(0)
    poller.stop()
    await vi.advanceTimersByTimeAsync(120_000)
    poller.refresh()
    expect(task).toHaveBeenCalledTimes(1)
  })
})
