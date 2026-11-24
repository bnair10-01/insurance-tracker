import { CATEGORIES, STATUSES, type Category, type Status } from '../types'

interface Props {
  category: Category | ''
  status: Status | ''
  onCategory: (value: Category | '') => void
  onStatus: (value: Status | '') => void
}

const selectClass = 'rounded border border-slate-300 bg-white px-3 py-1.5 text-sm'

export function FilterBar({ category, status, onCategory, onStatus }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <select className={selectClass} value={category} onChange={(e) => onCategory(e.target.value as Category | '')}>
        <option value="">All categories</option>
        {CATEGORIES.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
      <select className={selectClass} value={status} onChange={(e) => onStatus(e.target.value as Status | '')}>
        <option value="">All statuses</option>
        {STATUSES.map((value) => (
          <option key={value} value={value}>
            {value.replace('_', ' ')}
          </option>
        ))}
      </select>
    </div>
  )
}
