import type { InsuranceItem } from '../types'
import { StatusBadge } from './StatusBadge'

interface Props {
  items: InsuranceItem[]
  onSelect: (item: InsuranceItem) => void
}

function coveragePeriod(item: InsuranceItem): string {
  return item.coverage_end ? `${item.coverage_start} → ${item.coverage_end}` : `${item.coverage_start} → no end date`
}

function contactLines(item: InsuranceItem): string[] {
  const { phone, email, website, agent_name } = item.provider_contact
  return [phone, email, website, agent_name].filter((value): value is string => Boolean(value))
}

export function ItemsTable({ items, onSelect }: Props) {
  if (items.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
        No policies yet. Upload a policy PDF to get started.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">Item</th>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Coverage period</th>
            <th className="px-4 py-3">Provider</th>
            <th className="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              onClick={() => onSelect(item)}
              className="cursor-pointer border-b border-slate-100 last:border-0 hover:bg-slate-50"
            >
              <td className="px-4 py-3 font-medium text-slate-900">{item.item_name}</td>
              <td className="px-4 py-3 text-slate-600">{item.category}</td>
              <td className="px-4 py-3 text-slate-600">{coveragePeriod(item)}</td>
              <td className="px-4 py-3 text-slate-600">
                <div>{item.provider_name}</div>
                {contactLines(item).map((line) => (
                  <div key={line} className="text-xs text-slate-500">
                    {line}
                  </div>
                ))}
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={item.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
