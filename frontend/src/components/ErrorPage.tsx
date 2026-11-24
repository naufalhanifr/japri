import { ButtonLink } from './Button'

export type ErrorKind = 'not_found' | 'rate_limited' | 'failed'

const COPY: Record<ErrorKind, { code: string; title: string; body: string }> = {
  not_found: {
    code: '404',
    title: 'Halaman tidak ditemukan',
    body: 'Alamat yang Anda buka tidak ada atau sudah dipindahkan.',
  },
  rate_limited: {
    code: '429',
    title: 'Terlalu banyak permintaan',
    body: 'Anda mengirim terlalu banyak permintaan dalam waktu singkat. Tunggu sebentar, lalu coba lagi.',
  },
  failed: {
    code: 'Galat',
    title: 'Halaman belum bisa dimuat',
    body: 'Terjadi gangguan saat mengambil data. Periksa koneksi Anda, lalu coba lagi.',
  },
}

export function ErrorPage({ kind }: { kind: ErrorKind }) {
  const { code, title, body } = COPY[kind]
  return (
    <section className="error-page" aria-labelledby="error-title">
      <p className="error-page__code">{code}</p>
      <h1 id="error-title" tabIndex={-1} className="error-page__title">{title}</h1>
      <p className="error-page__body">{body}</p>
      <ButtonLink to="/" variant="primary">Kembali ke Dashboard</ButtonLink>
    </section>
  )
}
