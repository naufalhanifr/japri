const fromEnv = Number(import.meta.env.VITE_POLL_INTERVAL_MS)

export const POLL_INTERVAL_MS = Number.isFinite(fromEnv) && fromEnv >= 1000 ? fromEnv : 30_000
export const MAX_RANGE_DAYS = 31
export const DEFAULT_HOUR_START = 8
export const DEFAULT_HOUR_END = 17
