import { Route, Routes, useLocation } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Header } from './components/Header'
import { ToastProvider } from './components/Toast'
import { Dashboard } from './pages/Dashboard'
import { ErrorRoute, ErrorView } from './pages/ErrorRoute'
import { Riwayat } from './pages/Riwayat'

export function App() {
  const { pathname } = useLocation()
  return (
    <ToastProvider>
      <a className="skip-link" href="#main">Lewati ke konten</a>
      <Header />
      <ErrorBoundary key={pathname}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/riwayat" element={<Riwayat />} />
          <Route path="/galat/:kode" element={<ErrorRoute />} />
          <Route path="*" element={<ErrorView kind="not_found" />} />
        </Routes>
      </ErrorBoundary>
    </ToastProvider>
  )
}
