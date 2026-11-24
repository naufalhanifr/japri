export function DashboardSkeleton() {
  return (
    <div className="skeleton-page" aria-busy="true">
      <p className="visually-hidden" role="status">Memuat dashboard</p>
      <dl className="summary-grid" aria-hidden="true">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="summary-card summary-card--skeleton">
            <span className="skeleton skeleton--line skeleton--short" />
            <span className="skeleton skeleton--number" />
          </div>
        ))}
      </dl>
      <ul className="driver-grid" aria-hidden="true">
        {Array.from({ length: 8 }, (_, i) => (
          <li key={i} className="driver-card driver-card--skeleton">
            <span className="skeleton skeleton--line" />
            <span className="skeleton skeleton--line skeleton--short" />
            <span className="skeleton skeleton--block" />
          </li>
        ))}
      </ul>
      <div className="panel" aria-hidden="true">
        <span className="skeleton skeleton--line skeleton--short" />
        <span className="skeleton skeleton--timeline" />
      </div>
    </div>
  )
}
