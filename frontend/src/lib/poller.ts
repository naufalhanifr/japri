export interface PollerOptions {
  /** Returns a minimum delay (ms) before the next run, e.g. Retry-After from a 429. */
  task: (signal: AbortSignal) => Promise<number | void>
  intervalMs: number
  isHidden?: () => boolean
  target?: Pick<Document, 'addEventListener' | 'removeEventListener'>
}

export interface Poller {
  start: () => void
  stop: () => void
  refresh: () => void
}

export function createPoller(options: PollerOptions): Poller {
  const { task, intervalMs } = options
  const target = options.target ?? document
  const isHidden = options.isHidden ?? (() => document.visibilityState === 'hidden')

  let timer: ReturnType<typeof setTimeout> | null = null
  let controller: AbortController | null = null
  let running = false
  let generation = 0

  const clearTimer = () => {
    if (timer !== null) clearTimeout(timer)
    timer = null
  }

  const abortInFlight = () => {
    controller?.abort()
    controller = null
  }

  const schedule = (delayMs: number) => {
    clearTimer()
    if (!running || isHidden()) return
    timer = setTimeout(run, delayMs)
  }

  async function run() {
    clearTimer()
    if (!running) return
    abortInFlight()
    const current = new AbortController()
    controller = current
    const mine = ++generation
    let minDelay = 0
    try {
      const result = await task(current.signal)
      if (typeof result === 'number') minDelay = result
    } catch {
      // The task reports its own failures; the loop keeps going.
    }
    if (mine !== generation || current.signal.aborted) return
    controller = null
    schedule(Math.max(intervalMs, minDelay))
  }

  const onVisibilityChange = () => {
    if (!running) return
    if (isHidden()) {
      clearTimer()
      abortInFlight()
      generation++
    } else {
      void run()
    }
  }

  return {
    start() {
      if (running) return
      running = true
      target.addEventListener('visibilitychange', onVisibilityChange)
      if (!isHidden()) void run()
    },
    stop() {
      running = false
      target.removeEventListener('visibilitychange', onVisibilityChange)
      clearTimer()
      abortInFlight()
      generation++
    },
    refresh() {
      if (running) void run()
    },
  }
}
