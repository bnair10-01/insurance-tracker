import type { Status } from '../types'

const STYLES: Record<Status, { label: string; className: string }> = {
  active: { label: 'Active', className: 'bg-emerald-100 text-emerald-800' },
  upcoming: { label: 'Upcoming', className: 'bg-sky-100 text-sky-800' },
  expiring_soon: { label: 'Expiring soon', className: 'bg-amber-100 text-amber-800' },
  expired: { label: 'Expired', className: 'bg-red-100 text-red-800' },
  unknown: { label: 'Unknown', className: 'bg-slate-200 text-slate-700' },
}

export function StatusBadge({ status }: { status: Status }) {
  const { label, className } = STYLES[status]
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  )
}
