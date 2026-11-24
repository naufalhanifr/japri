import { useEffect, useId, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Banner } from './Banner'
import { Button } from './Button'
import { Icon } from './Icon'

export function SessionExpiredDialog() {
  const { state, acknowledgeExpired } = useAuth()
  const open = state.status === 'expired'
  const dialogRef = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const dialog = dialogRef.current
    if (open && dialog && !dialog.open) dialog.showModal()
  }, [open])

  const proceed = () => {
    acknowledgeExpired()
    navigate('/masuk', { replace: true, state: { expired: true, from: location.pathname + location.search } })
  }

  if (!open) return null
  return (
    <dialog ref={dialogRef} className="detail session-dialog" aria-labelledby={titleId} onCancel={(e) => e.preventDefault()}>
      <div className="detail__inner">
        <div className="session-dialog__head">
          <h2 id={titleId} className="detail__title">Sesi berakhir</h2>
          <button type="button" className="icon-button" aria-label="Tutup dan buka halaman masuk" onClick={proceed}>
            <Icon name="close" size={16} />
          </button>
        </div>
        <Banner tone="warning" title="Silakan login lagi untuk melanjutkan.">
          Isian yang belum disimpan tidak ikut tersimpan, jadi perlu diisi ulang setelah masuk.
        </Banner>
        <div className="detail__actions">
          <Button variant="primary" onClick={proceed} autoFocus>
            <Icon name="lock" size={16} />
            Login ulang
          </Button>
        </div>
      </div>
    </dialog>
  )
}
