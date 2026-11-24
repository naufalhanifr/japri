import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TODAY, type Selection } from '../lib/selection'
import { DatePicker } from './DatePicker'

const today = '2026-11-24'

function setup(selection: Selection = TODAY) {
  const onChange = vi.fn()
  render(<DatePicker selection={selection} today={today} onChange={onChange} />)
  return { onChange, user: userEvent.setup() }
}

async function openRange(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: 'Pilih tanggal' }))
  await user.click(screen.getByLabelText('Rentang'))
}

const setDate = (label: string, value: string) => {
  const input = screen.getByLabelText(label) as HTMLInputElement
  input.focus()
  return userEvent.clear(input).then(() => userEvent.type(input, value))
}

describe('DatePicker', () => {
  it('steps one day back and forward', async () => {
    const { onChange, user } = setup()
    await user.click(screen.getByRole('button', { name: 'Tanggal sebelumnya' }))
    expect(onChange).toHaveBeenLastCalledWith({ kind: 'date', date: '2026-11-23' })
    await user.click(screen.getByRole('button', { name: 'Tanggal berikutnya' }))
    expect(onChange).toHaveBeenLastCalledWith({ kind: 'date', date: '2026-11-25' })
  })

  it('disables the arrows for a range', () => {
    setup({ kind: 'range', start: '2026-11-20', end: '2026-11-26' })
    expect(screen.getByRole('button', { name: 'Tanggal sebelumnya' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Tanggal berikutnya' })).toBeDisabled()
  })

  it('applies a valid range and shows its length', async () => {
    const { onChange, user } = setup()
    await openRange(user)
    await setDate('Tanggal mulai', '2026-11-20')
    await setDate('Tanggal akhir', '2026-11-26')
    expect(screen.getByText('20 Nov - 26 Nov 2026 (7 hari)')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Terapkan' }))
    expect(onChange).toHaveBeenCalledWith({ kind: 'range', start: '2026-11-20', end: '2026-11-26' })
  })

  it('blocks a range where the end is before the start', async () => {
    const { onChange, user } = setup()
    await openRange(user)
    await setDate('Tanggal mulai', '2026-11-20')
    await setDate('Tanggal akhir', '2026-11-18')
    expect(screen.getByText('Mulai 20 Nov, akhir 18 Nov')).toBeInTheDocument()
    expect(screen.getByText('Tanggal akhir tidak boleh sebelum tanggal mulai.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Terapkan' })).toBeDisabled()
    expect(screen.getByLabelText('Tanggal akhir')).toBeInvalid()
    expect(onChange).not.toHaveBeenCalled()
  })

  it('blocks a range longer than 31 days', async () => {
    const { user } = setup()
    await openRange(user)
    await setDate('Tanggal mulai', '2026-11-01')
    await setDate('Tanggal akhir', '2026-12-02')
    expect(screen.getByText('Rentang maksimal 31 hari.', { selector: 'span' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Terapkan' })).toBeDisabled()
  })

  it('closes with Escape and returns focus to the trigger', async () => {
    const { user } = setup()
    const trigger = screen.getByRole('button', { name: 'Pilih tanggal' })
    await user.click(trigger)
    expect(screen.getByRole('dialog', { name: 'Pilih tanggal' })).toBeInTheDocument()
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(trigger).toHaveFocus()
  })

  it('offers a way back to today when another date is shown', async () => {
    const { onChange, user } = setup({ kind: 'date', date: '2026-11-20' })
    await user.click(screen.getByRole('button', { name: 'Kembali ke hari ini' }))
    expect(onChange).toHaveBeenCalledWith(TODAY)
  })
})
