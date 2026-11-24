import { ButtonLink } from '../components/Button'
import { usePageTitle } from '../hooks/usePageTitle'

export function Riwayat() {
  usePageTitle('Riwayat')
  return (
    <main id="main" className="page" tabIndex={-1}>
      <h1 className="page__title">Riwayat</h1>
      <section className="state-panel">
        <h2 className="state-panel__title">Daftar lengkap belum tersedia</h2>
        <p className="state-panel__body">
          Halaman ini disiapkan di tahap berikutnya. Untuk sementara, lima booking selesai terbaru ada di Dashboard.
        </p>
        <ButtonLink to="/" variant="primary">Kembali ke Dashboard</ButtonLink>
      </section>
    </main>
  )
}
