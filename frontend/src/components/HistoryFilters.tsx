import { HISTORY_MAX_RANGE_DAYS } from '../config'
import type { DriverOptionsState } from '../hooks/useHistory'
import type { HistoryFilters as Filters, HistoryStatus } from '../lib/historyQuery'
import { dateFilterLabel, hasFilters } from '../lib/historyQuery'
import { Button } from './Button'
import { DateRangePopover } from './DateRangePopover'
import { Icon } from './Icon'

interface Props {
  filters: Filters
  drivers: DriverOptionsState
  today: string
  rangeProblem: string | null
  onChange: (next: Filters) => void
  onReset: () => void
  onRetryDrivers: () => void
}

const STATUS_OPTIONS: { value: HistoryStatus | ''; label: string }[] = [
  { value: '', label: 'Selesai dan Dibatalkan' },
  { value: 'selesai', label: 'Selesai' },
  { value: 'dibatalkan', label: 'Dibatalkan' },
]

export function HistoryFilters({ filters, drivers, today, rangeProblem, onChange, onReset, onRetryDrivers }: Props) {
  const active = hasFilters(filters)
  const hasDates = filters.from !== null || filters.to !== null
  const value = filters.from && filters.to ? { start: filters.from, end: filters.to } : null

  return (
    <section className="panel" aria-label="Filter riwayat">
      <div className="filters">
        <div className="field">
          <label className="field__label" htmlFor="filter-driver">Driver</label>
          <select
            id="filter-driver"
            className="field__input"
            value={filters.driverId ?? ''}
            onChange={(e) => onChange({ ...filters, driverId: e.target.value ? Number(e.target.value) : null })}
          >
            <option value="">Semua driver</option>
            {drivers.status === 'loading' && filters.driverId !== null && (
              <option value={filters.driverId}>Memuat driver...</option>
            )}
            {drivers.status === 'ready' &&
              drivers.drivers.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}{d.is_active ? '' : ' (nonaktif)'}
                </option>
              ))}
            {drivers.status === 'error' && filters.driverId !== null && (
              <option value={filters.driverId}>Driver terpilih</option>
            )}
          </select>
          {drivers.status === 'error' && (
            <p className="field__error" role="alert">
              <Icon name="overdue" size={14} />
              Daftar driver belum bisa dimuat.
              <button type="button" className="text-link text-link--button" onClick={onRetryDrivers}>Coba lagi</button>
            </p>
          )}
        </div>

        <div className="field">
          <span className="field__label" id="filter-date-label">Tanggal <span className="field__opt">(opsional)</span></span>
          <div className="picker filters__date">
            <DateRangePopover
              align="left"
              triggerClassName="btn btn--secondary btn--block"
              triggerProps={{ 'aria-labelledby': 'filter-date-label filter-date', id: 'filter-date' }}
              trigger={
                <>
                  <Icon name="calendar" size={18} />
                  {dateFilterLabel(filters.from, filters.to)}
                </>
              }
              value={value}
              today={today}
              maxDays={HISTORY_MAX_RANGE_DAYS}
              onApply={({ start, end }) => onChange({ ...filters, from: start, to: end })}
            />
          </div>
          {hasDates && (
            <button
              type="button"
              className="text-link text-link--button"
              onClick={() => onChange({ ...filters, from: null, to: null })}
            >
              Hapus tanggal
            </button>
          )}
          {rangeProblem && (
            <p className="field__error" role="alert">
              <Icon name="overdue" size={14} />
              {rangeProblem}
            </p>
          )}
        </div>

        <div className="field">
          <label className="field__label" htmlFor="filter-status">Status</label>
          <select
            id="filter-status"
            className="field__input"
            value={filters.status ?? ''}
            onChange={(e) => onChange({ ...filters, status: (e.target.value || null) as HistoryStatus | null })}
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        <div className="field filters__reset">
          <Button variant="secondary" disabled={!active} onClick={onReset}>Hapus filter</Button>
        </div>
      </div>
    </section>
  )
}
