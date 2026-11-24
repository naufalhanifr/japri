import type { ReactNode } from 'react'
import { Icon, type IconName } from './Icon'

type Tone = 'info' | 'warning' | 'danger'

export function Banner({
  tone,
  title,
  children,
  action,
  role,
  icon,
}: {
  tone: Tone
  title: string
  children?: ReactNode
  action?: ReactNode
  role?: 'status' | 'alert'
  icon?: IconName
}) {
  return (
    <div className={`banner banner--${tone}`} role={role ?? (tone === 'danger' ? 'alert' : 'status')}>
      <Icon name={icon ?? (tone === 'info' ? 'info' : 'overdue')} size={20} />
      <div className="banner__text">
        <p className="banner__title">{title}</p>
        {children && <p className="banner__body">{children}</p>}
      </div>
      {action}
    </div>
  )
}
