import type { ReactNode } from 'react'

export type IconName =
  | 'running' | 'standby' | 'cuti' | 'scheduled' | 'done' | 'cancelled' | 'overdue'
  | 'info' | 'calendar' | 'prev' | 'next' | 'menu' | 'close' | 'lock' | 'logout' | 'offline'

const SOLID = { fill: 'currentColor' }
const LINE = { fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'butt' as const, strokeLinejoin: 'miter' as const }

const GLYPHS: Record<IconName, ReactNode> = {
  running: <path d="M4.5 2.5v11l8.5-5.5z" {...SOLID} />,
  standby: <circle cx="8" cy="8" r="4.5" {...SOLID} />,
  cuti: (
    <>
      <circle cx="8" cy="8" r="5.25" {...LINE} />
      <path d="M8 2.75a5.25 5.25 0 0 0 0 10.5z" {...SOLID} />
    </>
  ),
  scheduled: (
    <>
      <circle cx="8" cy="8" r="5.25" {...LINE} />
      <path d="M8 4.8v3.5l2.2 1.3" {...LINE} strokeWidth={1.8} />
    </>
  ),
  done: <path d="M3 8.6l3.3 3.3L13.2 4.6" {...LINE} strokeWidth={2.4} />,
  cancelled: <path d="M3.8 3.8l8.4 8.4M12.2 3.8l-8.4 8.4" {...LINE} strokeWidth={2.4} />,
  overdue: (
    <>
      <path d="M8 1.6l6.8 12H1.2z" {...SOLID} />
      <path d="M8 6v3.6" stroke="var(--jp-white)" strokeWidth={1.8} />
      <circle cx="8" cy="11.6" r="1" fill="var(--jp-white)" />
    </>
  ),
  info: (
    <>
      <circle cx="8" cy="8" r="6.5" {...SOLID} />
      <path d="M8 7.2v4" stroke="var(--jp-white)" strokeWidth={1.8} />
      <circle cx="8" cy="4.9" r="1" fill="var(--jp-white)" />
    </>
  ),
  calendar: (
    <>
      <path d="M2.5 4.2h11v9.3h-11z" {...LINE} strokeWidth={1.6} />
      <path d="M2.5 7.2h11M5.2 2.2v3M10.8 2.2v3" {...LINE} strokeWidth={1.6} />
    </>
  ),
  prev: <path d="M10 3L5 8l5 5" {...LINE} strokeWidth={2.2} />,
  next: <path d="M6 3l5 5-5 5" {...LINE} strokeWidth={2.2} />,
  menu: <path d="M2 4h12M2 8h12M2 12h12" {...LINE} strokeWidth={2} />,
  close: <path d="M3.5 3.5l9 9M12.5 3.5l-9 9" {...LINE} strokeWidth={2} />,
  lock: (
    <>
      <path d="M3 7.2h10v6.6H3z" {...LINE} strokeWidth={1.6} />
      <path d="M5.2 7.2V5a2.8 2.8 0 0 1 5.6 0v2.2" {...LINE} strokeWidth={1.6} />
    </>
  ),
  logout: (
    <>
      <path d="M6.5 2.5H2.5v11h4" {...LINE} strokeWidth={1.6} />
      <path d="M6.5 8h7M10.8 5.2L13.6 8l-2.8 2.8" {...LINE} strokeWidth={1.6} />
    </>
  ),
  offline: (
    <>
      <path d="M2 6.2a8.5 8.5 0 0 1 12 0M4.4 8.8a5.2 5.2 0 0 1 7.2 0" {...LINE} strokeWidth={1.6} />
      <circle cx="8" cy="11.6" r="1" {...SOLID} />
      <path d="M2.5 2.5l11 11" {...LINE} strokeWidth={1.8} />
    </>
  ),
}

export function Icon({ name, size = 16 }: { name: IconName; size?: number }) {
  return (
    <svg className="icon" width={size} height={size} viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      {GLYPHS[name]}
    </svg>
  )
}
