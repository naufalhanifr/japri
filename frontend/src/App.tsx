import { Route, Routes, useLocation } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { RequireAdmin } from './auth/RequireAdmin'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Header } from './components/Header'
import { SessionExpiredDialog } from './components/SessionExpiredDialog'
import { ToastProvider } from './components/Toast'
import { AdminPlaceholder } from './pages/AdminPlaceholder'
import { Dashboard } from './pages/Dashboard'
import { ErrorRoute, ErrorView } from './pages/ErrorRoute'
import { Masuk } from './pages/Masuk'
import { Riwayat } from './pages/Riwayat'

export function App() {
  const { pathname } = useLocation()
  return (
    <ToastProvider>
      <AuthProvider>
        <a className="skip-link" href="#main">Lewati ke konten</a>
        <Header />
        <ErrorBoundary key={pathname}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/riwayat" element={<Riwayat />} />
            <Route path="/masuk" element={<Masuk />} />
            <Route path="/admin/booking" element={<RequireAdmin><AdminPlaceholder title="Booking" /></RequireAdmin>} />
            <Route path="/admin/driver" element={<RequireAdmin><AdminPlaceholder title="Kelola driver" /></RequireAdmin>} />
            <Route path="/galat/:kode" element={<ErrorRoute />} />
            <Route path="*" element={<ErrorView kind="not_found" />} />
          </Routes>
        </ErrorBoundary>
        <SessionExpiredDialog />
      </AuthProvider>
    </ToastProvider>
  )
}
