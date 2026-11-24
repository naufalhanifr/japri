import { useEffect, useId, useRef, useState } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button, ButtonLink } from './Button'
import { Icon } from './Icon'
import { useToast } from './Toast'

const PUBLIC_LINKS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/riwayat', label: 'Riwayat', end: false },
]

const ADMIN_LINKS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/admin/booking', label: 'Booking', end: false },
  { to: '/admin/driver', label: 'Kelola driver', end: false },
  { to: '/riwayat', label: 'Riwayat', end: false },
]

export function Header() {
  const [open, setOpen] = useState(false)
  const menuId = useId()
  const buttonRef = useRef<HTMLButtonElement>(null)
  const location = useLocation()
  const navigate = useNavigate()
  const toast = useToast()
  const { state, logout } = useAuth()
  const [leaving, setLeaving] = useState(false)
  const admin = state.status === 'admin' ? state.admin : null
  const links = admin ? ADMIN_LINKS : PUBLIC_LINKS
  const showLogin = state.status === 'anonymous' && location.pathname !== '/masuk'
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

  const onLogout = async () => {
    setLeaving(true)
    try {
      await logout()
      navigate('/', { replace: true })
    } catch {
      toast('Belum bisa keluar. Coba lagi.')
    } finally {
      setLeaving(false)
    }
  }

  return (
    <header className={admin ? 'site-header site-header--admin' : 'site-header'}>
      <div className="site-header__bar">
        <div className="site-header__lead">
          <NavLink to="/" className="site-header__brand">Jadwal Driver</NavLink>
          {admin && <span className="mode-chip">Admin</span>}
        </div>
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
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className="site-header__link">
              {link.label}
            </NavLink>
          ))}
          {admin && (
            <>
              <span className="site-header__who">{admin.display_name}</span>
              <Button className="site-header__logout" onClick={onLogout} disabled={leaving}>
                <Icon name="logout" size={16} />
                Keluar
              </Button>
            </>
          )}
          {showLogin && (
            <ButtonLink to="/masuk" className="site-header__login">
              <Icon name="lock" size={16} />
              Login Admin
            </ButtonLink>
          )}
        </nav>
      </div>
    </header>
  )
}
