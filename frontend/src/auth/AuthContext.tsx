import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchAdminMe, loginAdmin, logoutAdmin, setCsrfToken, setSessionLostHandler } from '../api/admin'
import { isAbortError } from '../api/client'
import type { AdminProfile } from '../api/types'

export type AuthState =
  | { status: 'loading' }
  | { status: 'anonymous'; after?: 'logout' | 'expired' }
  | { status: 'admin'; admin: AdminProfile }
  | { status: 'expired' }

interface AuthValue {
  state: AuthState
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  acknowledgeExpired: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth harus dipakai di dalam AuthProvider')
  return value
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()
    fetchAdminMe(controller.signal).then(
      (admin) => setState({ status: 'admin', admin }),
      (error) => {
        if (!isAbortError(error)) setState({ status: 'anonymous' })
      },
    )
    return () => controller.abort()
  }, [])

  useEffect(() => {
    setSessionLostHandler(() => {
      setCsrfToken(null)
      setState((current) => (current.status === 'admin' ? { status: 'expired' } : current))
    })
    return () => setSessionLostHandler(null)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const admin = await loginAdmin(email, password)
    setState({ status: 'admin', admin })
  }, [])

  const logout = useCallback(async () => {
    await logoutAdmin()
    setState({ status: 'anonymous', after: 'logout' })
  }, [])

  const acknowledgeExpired = useCallback(() => {
    setState((current) => (current.status === 'expired' ? { status: 'anonymous', after: 'expired' } : current))
  }, [])

  const value = useMemo(() => ({ state, login, logout, acknowledgeExpired }), [state, login, logout, acknowledgeExpired])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
