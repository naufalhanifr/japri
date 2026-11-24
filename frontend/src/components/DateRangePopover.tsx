import { useCallback, useEffect, useId, useRef, useState, type ButtonHTMLAttributes, type ReactNode } from 'react'
import {
  clampDate, monthHasDates, monthOf, monthTitle, monthWeeks, moveFocus, shiftMonth, WEEKDAYS, type DayKey,
} from '../lib/calendar'
import { formatLongDate, formatRangeLabel, formatShortDate, inclusiveDays, validateRange } from '../lib/date'
import { Button } from './Button'
import { Icon } from './Icon'

export interface DateSpan {
  start: string
  end: string
}

interface Props {
  trigger: ReactNode
  triggerClassName?: string
  triggerProps?: ButtonHTMLAttributes<HTMLButtonElement>
  value: DateSpan | null
  today: string
  maxDays: number
  onApply: (span: DateSpan) => void
  align?: 'left' | 'right'
}

type Mode = 'date' | 'range'

const NAV_KEYS = new Set<string>(['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'])

export function DateRangePopover({
  trigger, triggerClassName = 'btn btn--secondary', triggerProps, value, today, maxDays, onApply, align = 'right',
}: Props) {
  const [open, setOpen] = useState(false)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)
  const panelId = useId()

  const close = useCallback((restoreFocus = true) => {
    setOpen(false)
    if (restoreFocus) triggerRef.current?.focus()
  }, [])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') close()
    }
    const onPointer = (event: PointerEvent) => {
      const target = event.target as Node
      if (!panelRef.current?.contains(target) && !triggerRef.current?.contains(target)) close(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('pointerdown', onPointer)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('pointerdown', onPointer)
    }
  }, [open, close])

  return (
    <>
      <button
        {...triggerProps}
        ref={triggerRef}
        type="button"
        className={triggerClassName}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={open ? panelId : undefined}
        onClick={() => setOpen((v) => !v)}
      >
        {trigger}
      </button>
      {open && (
        <>
          <div className="picker__backdrop" aria-hidden="true" />
          <CalendarPanel
            id={panelId}
            panelRef={panelRef}
            align={align}
            value={value}
            today={today}
            maxDays={maxDays}
            onCancel={() => close()}
            onApply={(span) => {
              onApply(span)
              close()
            }}
          />
        </>
      )}
    </>
  )
}

function CalendarPanel({
  id, panelRef, align, value, today, maxDays, onCancel, onApply,
}: {
  id: string
  panelRef: React.RefObject<HTMLDivElement | null>
  align: 'left' | 'right'
  value: DateSpan | null
  today: string
  maxDays: number
  onCancel: () => void
  onApply: (span: DateSpan) => void
}) {
  const [mode, setMode] = useState<Mode>(value && value.start !== value.end ? 'range' : 'date')
  const [start, setStart] = useState<string | null>(value?.start ?? null)
  const [end, setEnd] = useState<string | null>(value ? value.end : null)
  const [focusDate, setFocusDate] = useState(clampDate(value?.start ?? today))
  const gridRef = useRef<HTMLTableElement>(null)
  const shouldFocus = useRef(true)
  const errorId = useId()
  const month = monthOf(focusDate)

  useEffect(() => {
    if (!shouldFocus.current) return
    shouldFocus.current = false
    gridRef.current?.querySelector<HTMLButtonElement>(`[data-date="${focusDate}"]`)?.focus()
  }, [focusDate])

  const rangeCheck = mode === 'range' && start && end ? validateRange(start, end, maxDays) : null
  const canApply = mode === 'date' ? start !== null : rangeCheck?.ok === true
  const ordered = start !== null && end !== null && start <= end

  const pick = (date: string) => {
    setFocusDate(date)
    if (mode === 'date') {
      setStart(date)
      setEnd(date)
    } else if (start !== null && end === null) {
      setEnd(date)
    } else {
      setStart(date)
      setEnd(null)
    }
  }

  const changeMode = (next: Mode) => {
    if (next === mode) return
    setMode(next)
    if (next === 'date') {
      setEnd(start)
    } else {
      setStart(null)
      setEnd(null)
    }
  }

  const goToMonth = (delta: number) => {
    shouldFocus.current = false
    setFocusDate(moveFocus(focusDate, delta < 0 ? 'PageUp' : 'PageDown'))
  }

  const onDayKeyDown = (event: React.KeyboardEvent) => {
    if (!NAV_KEYS.has(event.key)) return
    event.preventDefault()
    shouldFocus.current = true
    setFocusDate(moveFocus(focusDate, event.key as DayKey))
  }

  const apply = () => {
    if (!canApply || start === null) return
    onApply({ start, end: mode === 'date' ? start : (end as string) })
  }

  const inRange = (date: string) => ordered && date > (start as string) && date < (end as string)
  const isEdge = (date: string) => date === start || date === end

  return (
    <div
      id={id}
      ref={panelRef}
      className={`picker__panel picker__panel--${align}`}
      role="dialog"
      aria-label="Pilih tanggal"
    >
      <fieldset className="segmented">
        <legend className="visually-hidden">Jenis pilihan</legend>
        <label className={mode === 'date' ? 'is-selected' : ''}>
          <input type="radio" name={`${id}-mode`} checked={mode === 'date'} onChange={() => changeMode('date')} />
          Satu tanggal
        </label>
        <label className={mode === 'range' ? 'is-selected' : ''}>
          <input type="radio" name={`${id}-mode`} checked={mode === 'range'} onChange={() => changeMode('range')} />
          Rentang
        </label>
      </fieldset>

      <div className="cal__head">
        <button
          type="button"
          className="icon-button"
          aria-label="Bulan sebelumnya"
          disabled={!monthHasDates(shiftMonth(month, -1))}
          onClick={() => goToMonth(-1)}
        >
          <Icon name="prev" size={18} />
        </button>
        <strong id={`${id}-month`} aria-live="polite">{monthTitle(month)}</strong>
        <button
          type="button"
          className="icon-button"
          aria-label="Bulan berikutnya"
          disabled={!monthHasDates(shiftMonth(month, 1))}
          onClick={() => goToMonth(1)}
        >
          <Icon name="next" size={18} />
        </button>
      </div>

      <table ref={gridRef} className="cal" role="grid" aria-labelledby={`${id}-month`} onKeyDown={onDayKeyDown}>
        <thead>
          <tr>
            {WEEKDAYS.map((d) => (
              <th key={d.short} scope="col" abbr={d.long}>{d.short}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {monthWeeks(month).map((week, i) => (
            <tr key={i}>
              {week.map((date, j) => {
                if (!date) return <td key={j} />
                const edge = isEdge(date)
                const classes = ['cal__day', edge && 'is-edge', inRange(date) && 'is-in', date === today && 'is-today']
                return (
                  <td key={date} aria-selected={edge || inRange(date)}>
                    <button
                      type="button"
                      className={classes.filter(Boolean).join(' ')}
                      data-date={date}
                      tabIndex={date === focusDate ? 0 : -1}
                      aria-label={formatLongDate(date)}
                      aria-current={date === today ? 'date' : undefined}
                      onClick={() => pick(date)}
                    >
                      {Number(date.slice(8, 10))}
                    </button>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div id={errorId} aria-live="polite" className="picker__status">
        {mode === 'date' && (
          <p className="picker__summary">{start ? formatLongDate(start) : 'Pilih satu tanggal.'}</p>
        )}
        {mode === 'range' && !start && <p className="picker__summary">Pilih tanggal mulai.</p>}
        {mode === 'range' && start && !end && (
          <p className="picker__summary">Mulai {formatShortDate(start)}. Pilih tanggal akhir.</p>
        )}
        {rangeCheck?.ok && start && end && (
          <p className="picker__summary">{formatRangeLabel(start, end)} ({inclusiveDays(start, end)} hari)</p>
        )}
        {rangeCheck?.ok === false && start && end && (
          <div className="picker__error">
            {rangeCheck.reason === 'end_before_start' && (
              <strong>Mulai {formatShortDate(start)}, akhir {formatShortDate(end)}</strong>
            )}
            <span>{rangeCheck.message}</span>
          </div>
        )}
      </div>
      {mode === 'range' && <p className="picker__hint">Rentang maksimal {maxDays} hari.</p>}

      <div className="picker__actions">
        <Button variant="ghost" onClick={onCancel}>Batal</Button>
        <Button variant="primary" disabled={!canApply} onClick={apply}>Terapkan</Button>
      </div>
    </div>
  )
}
