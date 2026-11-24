import { usePageTitle } from '../hooks/usePageTitle'

export function AdminPlaceholder({ title }: { title: string }) {
  usePageTitle(title)
  return (
    <main id="main" className="page" tabIndex={-1}>
      <h1 className="page__title">{title}</h1>
      <p className="page__lead">Halaman ini belum tersedia dan menyusul di tahap berikutnya.</p>
    </main>
  )
}
