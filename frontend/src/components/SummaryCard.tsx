export function SummaryCard({ label, value, tone }: { label: string; value: number | string; tone?: 'running' | 'standby' | 'cuti' }) {
  return (
    <div className={`summary-card${tone ? ` summary-card--${tone}` : ''}`}>
      <dt className="summary-card__label">{label}</dt>
      <dd className="summary-card__value">{value}</dd>
    </div>
  )
}
