import { useEffect, useId, useRef, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { Icon } from './Icon'

const LINKS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/riwayat', label: 'Riwayat', end: false },
]

export function Header() {
  const [open, setOpen] = useState(false)
  const menuId = useId()
  const buttonRef = useRef<HTMLButtonElement>(null)
  const location = useLocation()
  const [lastPath, setLastPath] = useState(location.pathname)

  if (lastPath !== location.pathname) {
    setLastPath(location.pathname)
    setOpen(false)
  }

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false)
        buttonRef.current?.focus()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open])

  return (
    <header className="site-header">
      <div className="site-header__bar">
        <NavLink to="/" className="site-header__brand">Jadwal Driver</NavLink>
        <button
          ref={buttonRef}
          type="button"
          className="site-header__menu-button"
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((v) => !v)}
        >
          <Icon name={open ? 'close' : 'menu'} size={20} />
          <span>Menu</span>
        </button>
        <nav id={menuId} className={`site-header__nav${open ? ' is-open' : ''}`} aria-label="Menu utama">
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className="site-header__link">
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
