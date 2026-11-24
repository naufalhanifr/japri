import { useParams } from 'react-router-dom'
import { ErrorPage, type ErrorKind } from '../components/ErrorPage'
import { usePageTitle } from '../hooks/usePageTitle'

const TITLES: Record<ErrorKind, string> = {
  not_found: 'Halaman tidak ditemukan',
  rate_limited: 'Terlalu banyak permintaan',
  failed: 'Halaman belum bisa dimuat',
}

export function kindFromParam(param: string | undefined): ErrorKind | null {
  if (param === '429') return 'rate_limited'
  if (param === 'gagal') return 'failed'
  return null
}

export function ErrorView({ kind }: { kind: ErrorKind }) {
  usePageTitle(TITLES[kind])
  return (
    <main id="main" className="page" tabIndex={-1}>
      <ErrorPage kind={kind} />
    </main>
  )
}

export function ErrorRoute() {
  const kind = kindFromParam(useParams().kode) ?? 'not_found'
  return <ErrorView kind={kind} />
}
