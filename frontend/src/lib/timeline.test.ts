import { describe, expect, it } from 'vitest'
import { booking } from '../test-fixtures'
import { layoutTimeline } from './timeline'

const DAY = '2026-11-24'
const at = (h: number, m = 0, date = DAY) => `${date}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00+07:00`
const item = (...bookings: ReturnType<typeof booking>[]) => [{ driver_id: 1, bookings }]

describe('layoutTimeline', () => {
  it('defaults to 08:00-17:00 when data fits inside', () => {
    const layout = layoutTimeline(item(booking({ id: 1, start_at: at(9), end_at: at(10) })), DAY, null)
    expect([layout.startHour, layout.endHour]).toEqual([8, 17])
    expect(layout.hours).toHaveLength(10)
  })

  it('widens the hour range to follow the data (E12)', () => {
    const layout = layoutTimeline(
      item(booking({ id: 1, start_at: at(6, 30), end_at: at(7) }), booking({ id: 2, start_at: at(18), end_at: at(20, 15) })),
      DAY,
      null,
    )
    expect([layout.startHour, layout.endHour]).toEqual([6, 21])
  })

  it('stacks overlapping bookings in separate lanes (E8)', () => {
    const layout = layoutTimeline(
      item(
        booking({ id: 1, start_at: at(9), end_at: at(12) }),
        booking({ id: 2, start_at: at(10), end_at: at(11) }),
        booking({ id: 3, start_at: at(12), end_at: at(13) }),
      ),
      DAY,
      null,
    )
    const lanes = layout.rows[0].lanes
    expect(lanes).toHaveLength(2)
    expect(lanes[0].map((b) => b.booking.id)).toEqual([1, 3])
    expect(lanes[1].map((b) => b.booking.id)).toEqual([2])
  })

  it('clips multi-day bookings and labels the day (E9)', () => {
    const multi = booking({ id: 1, start_at: at(10, 0, '2026-11-23'), end_at: at(15, 0, '2026-11-25') })
    const middle = layoutTimeline(item(multi), DAY, null).rows[0].lanes[0][0]
    expect(middle).toMatchObject({ clippedStart: true, clippedEnd: true, leftPct: 0, widthPct: 100 })
    expect(middle.dayInfo).toEqual({ day: 2, of: 3 })
    const first = layoutTimeline(item(multi), '2026-11-23', null).rows[0].lanes[0][0]
    expect(first.dayInfo).toEqual({ day: 1, of: 3 })
    expect(first.clippedStart).toBe(false)
    expect(layoutTimeline(item(multi), '2026-11-26', null).rows[0].lanes).toHaveLength(0)
  })

  it('does not widen the window for the clipped side of a multi-day bar', () => {
    const multi = booking({ id: 1, start_at: at(10, 0, '2026-11-23'), end_at: at(15, 0, '2026-11-25') })
    const layout = layoutTimeline(item(multi), DAY, null)
    expect([layout.startHour, layout.endHour]).toEqual([8, 17])
  })

  it('places the now-line only on the selected date and inside the window', () => {
    const data = item(booking({ id: 1, start_at: at(9), end_at: at(10) }))
    expect(layoutTimeline(data, DAY, at(12, 30))?.nowPct).toBeCloseTo(50)
    expect(layoutTimeline(data, DAY, at(12, 30, '2026-11-25')).nowPct).toBeNull()
    expect(layoutTimeline(data, DAY, null).nowPct).toBeNull()
  })

  it('returns an empty row for drivers without bookings that day', () => {
    const layout = layoutTimeline([{ driver_id: 5, bookings: [] }], DAY, null)
    expect(layout.rows).toEqual([{ driverId: 5, lanes: [] }])
  })
})
