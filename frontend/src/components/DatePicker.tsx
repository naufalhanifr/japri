import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { MAX_RANGE_DAYS } from '../config'
import { formatRangeLabel, inclusiveDays, MAX_DATE, MIN_DATE, formatShortDate, validateRange } from '../lib/date'
import { normalizeSelection, selectionBounds, shiftSelection, TODAY, type Selection } from '../lib/selection'
import { Button } from './Button'
import { Icon } from './Icon'

interface Props {
  selection: Selection
  today: string
  onChange: (selection: Selection) => void
}

type Mode = 'date' | 'range'

export function DatePicker({ selection, today, onChange }: Props) {
  const [open, setOpen] = useState(false)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)
  const panelId = useId()

  const previous = shiftSelection(selection, -1, today)
  const next = shiftSelection(selection, 1, today)

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
    <div className="picker">
      <div className="picker__bar">
        <button
          type="button"
          className="icon-button"
          aria-label="Tanggal sebelumnya"
          disabled={!previous}
          onClick={() => previous && onChange(previous)}
        >
          <Icon name="prev" size={18} />
        </button>
        <button
          ref={triggerRef}
          type="button"
          className="btn btn--secondary"
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-controls={open ? panelId : undefined}
          onClick={() => setOpen((v) => !v)}
        >
          <Icon name="calendar" size={18} />
          Pilih tanggal
        </button>
        <button
          type="button"
          className="icon-button"
          aria-label="Tanggal berikutnya"
          disabled={!next}
          onClick={() => next && onChange(next)}
        >
          <Icon name="next" size={18} />
        </button>
        {selection.kind === 'today' ? (
          <span className="chip" aria-label="Menampilkan hari ini">Hari ini</span>
        ) : (
          <Button variant="ghost" onClick={() => onChange(TODAY)}>Kembali ke hari ini</Button>
        )}
      </div>
      {open && (
        <PickerPanel
          id={panelId}
          panelRef={panelRef}
          selection={selection}
          today={today}
          onCancel={() => close()}
          onApply={(value) => {
            onChange(value)
            close()
          }}
        />
      )}
    </div>
  )
}

function PickerPanel({
  id,
  panelRef,
  selection,
  today,
  onCancel,
  onApply,
}: {
  id: string
  panelRef: React.RefObject<HTMLDivElement | null>
  selection: Selection
  today: string
  onCancel: () => void
  onApply: (selection: Selection) => void
}) {
  const bounds = selectionBounds(selection, today)
  const [mode, setMode] = useState<Mode>(selection.kind === 'range' ? 'range' : 'date')
  const [single, setSingle] = useState(bounds.start)
  const [start, setStart] = useState(bounds.start)
  const [end, setEnd] = useState(bounds.end)
  const firstFieldRef = useRef<HTMLInputElement>(null)
  const errorId = useId()

  useEffect(() => {
    firstFieldRef.current?.focus()
  }, [])

  const rangeCheck = mode === 'range' ? validateRange(start, end) : null
  const singleValid = mode === 'date' && /^\d{4}-\d{2}-\d{2}$/.test(single) && single >= MIN_DATE && single <= MAX_DATE
  const canApply = mode === 'date' ? singleValid : rangeCheck?.ok === true

  const apply = () => {
    if (!canApply) return
    onApply(mode === 'date' ? normalizeSelection(single, single, today) : normalizeSelection(start, end, today))
  }

  return (
    <div
      id={id}
      ref={panelRef}
      className="picker__panel"
      role="dialog"
      aria-label="Pilih tanggal"
      onKeyDown={(event) => {
        if (event.key === 'Enter' && (event.target as HTMLElement).tagName === 'INPUT') {
          event.preventDefault()
          apply()
        }
      }}
    >
      <fieldset className="segmented">
        <legend className="visually-hidden">Jenis pilihan</legend>
        <label className={mode === 'date' ? 'is-selected' : ''}>
          <input type="radio" name={`${id}-mode`} checked={mode === 'date'} onChange={() => setMode('date')} />
          Satu tanggal
        </label>
        <label className={mode === 'range' ? 'is-selected' : ''}>
          <input type="radio" name={`${id}-mode`} checked={mode === 'range'} onChange={() => setMode('range')} />
          Rentang
        </label>
      </fieldset>

      {mode === 'date' ? (
        <label className="field">
          <span className="field__label">Tanggal</span>
          <input
            ref={firstFieldRef}
            type="date"
            className="field__input"
            value={single}
            min={MIN_DATE}
            max={MAX_DATE}
            onChange={(e) => setSingle(e.target.value)}
          />
        </label>
      ) : (
        <>
          <div className="field-row">
            <label className="field">
              <span className="field__label">Tanggal mulai</span>
              <input
                ref={firstFieldRef}
                type="date"
                className="field__input"
                value={start}
                min={MIN_DATE}
                max={MAX_DATE}
                onChange={(e) => setStart(e.target.value)}
              />
            </label>
            <label className="field">
              <span className="field__label">Tanggal akhir</span>
              <input
                type="date"
                className="field__input"
                value={end}
                min={MIN_DATE}
                max={MAX_DATE}
                aria-invalid={rangeCheck?.ok === false}
                aria-describedby={rangeCheck?.ok === false ? errorId : undefined}
                onChange={(e) => setEnd(e.target.value)}
              />
            </label>
          </div>
          <p className="picker__hint">Rentang maksimal {MAX_RANGE_DAYS} hari.</p>
          <div id={errorId} aria-live="polite">
            {rangeCheck?.ok === false && (
              <div className="picker__error">
                {rangeCheck.reason === 'end_before_start' && (
                  <strong>Mulai {formatShortDate(start)}, akhir {formatShortDate(end)}</strong>
                )}
                <span>{rangeCheck.message}</span>
              </div>
            )}
            {rangeCheck?.ok && (
              <p className="picker__summary">{formatRangeLabel(start, end)} ({inclusiveDays(start, end)} hari)</p>
            )}
          </div>
        </>
      )}

      <div className="picker__actions">
        <Button variant="ghost" onClick={onCancel}>Batal</Button>
        <Button variant="primary" disabled={!canApply} onClick={apply}>Terapkan</Button>
      </div>
    </div>
  )
}
