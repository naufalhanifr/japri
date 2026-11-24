import { Component, type ReactNode } from 'react'
import { ErrorView } from '../pages/ErrorRoute'

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  render() {
    return this.state.failed ? <ErrorView kind="failed" /> : this.props.children
  }
}
