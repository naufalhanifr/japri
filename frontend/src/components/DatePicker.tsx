import { MAX_RANGE_DAYS } from '../config'
import { normalizeSelection, selectionBounds, shiftSelection, TODAY, type Selection } from '../lib/selection'
import { Button } from './Button'
import { DateRangePopover } from './DateRangePopover'
import { Icon } from './Icon'

interface Props {
  selection: Selection
  today: string
  onChange: (selection: Selection) => void
}

export function DatePicker({ selection, today, onChange }: Props) {
  const previous = shiftSelection(selection, -1, today)
  const next = shiftSelection(selection, 1, today)

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
        <DateRangePopover
          trigger={
            <>
              <Icon name="calendar" size={18} />
              Pilih tanggal
            </>
          }
          value={selectionBounds(selection, today)}
          today={today}
          maxDays={MAX_RANGE_DAYS}
          onApply={({ start, end }) => onChange(normalizeSelection(start, end, today))}
        />
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
    </div>
  )
}
