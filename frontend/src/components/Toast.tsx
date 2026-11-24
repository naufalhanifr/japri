import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { Icon } from './Icon'

interface ToastItem {
  id: number
  message: string
}

const ToastContext = createContext<(message: string) => void>(() => {})

export const TOAST_DURATION_MS = 5000

export function useToast() {
  return useContext(ToastContext)
}

let nextId = 1

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])
  const dismiss = useCallback((id: number) => setItems((list) => list.filter((t) => t.id !== id)), [])
  const show = useCallback((message: string) => setItems((list) => [...list, { id: nextId++, message }]), [])
  const value = useMemo(() => show, [show])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-region" role="status" aria-live="polite">
        {items.map((item) => (
          <ToastView key={item.id} item={item} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

function ToastView({ item, onDismiss }: { item: ToastItem; onDismiss: (id: number) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(item.id), TOAST_DURATION_MS)
    return () => clearTimeout(timer)
  }, [item.id, onDismiss])

  return (
    <div className="toast">
      <Icon name="done" size={16} />
      <span>{item.message}</span>
      <button type="button" className="toast__close" onClick={() => onDismiss(item.id)} aria-label="Tutup pemberitahuan">
        <Icon name="close" size={14} />
      </button>
    </div>
  )
}
