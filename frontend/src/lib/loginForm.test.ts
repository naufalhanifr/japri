import { describe, expect, it } from 'vitest'
import { safeReturnPath, validateLogin, waitLabel } from './loginForm'

describe('validateLogin', () => {
  it('accepts a normal email and password', () => {
    expect(validateLogin(' admin@contoh.id ', 'x')).toEqual({})
  })

  it('flags empty fields', () => {
    expect(validateLogin('', '')).toEqual({ email: 'Email wajib diisi.', password: 'Password wajib diisi.' })
  })

  it('flags email without a domain suffix', () => {
    expect(validateLogin('admin@contoh', 'x').email).toMatch(/Format email tidak valid/)
    expect(validateLogin('admin contoh.id', 'x').email).toMatch(/Format email tidak valid/)
  })

  it('does not trim the password', () => {
    expect(validateLogin('a@b.id', '   ')).toEqual({})
  })
})

describe('waitLabel', () => {
  it('rounds up to whole minutes', () => {
    expect(waitLabel(30)).toBe('kurang dari satu menit')
    expect(waitLabel(60)).toBe('1 menit')
    expect(waitLabel(61)).toBe('2 menit')
    expect(waitLabel(900)).toBe('15 menit')
  })
})

describe('safeReturnPath', () => {
  it('keeps internal paths only', () => {
    expect(safeReturnPath('/admin/booking')).toBe('/admin/booking')
    expect(safeReturnPath('//evil.example')).toBe('/')
    expect(safeReturnPath('https://evil.example')).toBe('/')
    expect(safeReturnPath('/masuk')).toBe('/')
    expect(safeReturnPath(undefined)).toBe('/')
    expect(safeReturnPath('/admin/booking?x=1')).toBe('/admin/booking?x=1')
  })

  it.each(['/\\evil.com', '/\t/evil.com', '//evil.com', 'https://evil.com', '/masuk', '/masuk?next=/'])(
    'rejects %j',
    (value) => {
      expect(safeReturnPath(value)).toBe('/')
    },
  )
})
