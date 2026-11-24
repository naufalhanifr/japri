import { Icon, type IconName } from './Icon'

export type StatusKind =
  | 'sedang_jalan' | 'standby' | 'cuti'
  | 'berjalan' | 'terjadwal' | 'selesai' | 'dibatalkan' | 'overdue'

const META: Record<StatusKind, { label: string; icon: IconName }> = {
  sedang_jalan: { label: 'Sedang jalan', icon: 'running' },
  standby: { label: 'Standby', icon: 'standby' },
  cuti: { label: 'Cuti', icon: 'cuti' },
  berjalan: { label: 'Berjalan', icon: 'running' },
  terjadwal: { label: 'Terjadwal', icon: 'scheduled' },
  selesai: { label: 'Selesai', icon: 'done' },
  dibatalkan: { label: 'Dibatalkan', icon: 'cancelled' },
  overdue: { label: 'Melewati jam selesai', icon: 'overdue' },
}

export function StatusBadge({ kind }: { kind: StatusKind }) {
  const { label, icon } = META[kind]
  return (
    <span className={`badge badge--${kind}`}>
      <Icon name={icon} size={14} />
      {label}
    </span>
  )
}
