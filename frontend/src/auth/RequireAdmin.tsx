import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

// Hanya untuk tampilan. Perlindungan sebenarnya ada di server: tiap route /api/admin wajib sesi.
export function RequireAdmin({ children }: { children: ReactNode }) {
  const { state } = useAuth()
  const location = useLocation()

  if (state.status === 'admin') return <>{children}</>
  if (state.status === 'anonymous') {
    if (state.after === 'logout') return <Navigate to="/" replace />
    const from = location.pathname + location.search
    return <Navigate to="/masuk" replace state={state.after === 'expired' ? { from, expired: true } : { from }} />
  }
  return (
    <main id="main" className="page" tabIndex={-1} aria-busy={state.status === 'loading'}>
      <div className="skeleton skeleton--line" />
    </main>
  )
}
