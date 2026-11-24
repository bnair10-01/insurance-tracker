import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { deleteItem, downloadDocument, listItems, updateItem } from '../api/items'
import { FilterBar } from '../components/FilterBar'
import { ItemsTable } from '../components/ItemsTable'
import { ReviewForm } from '../components/ReviewForm'
import type { Category, InsuranceItem, ItemFormValues, Status } from '../types'

function toFormValues(item: InsuranceItem): ItemFormValues {
  return {
    item_name: item.item_name,
    category: item.category,
    provider_name: item.provider_name,
    provider_contact: item.provider_contact,
    policy_number: item.policy_number,
    coverage_start: item.coverage_start,
    coverage_end: item.coverage_end,
    premium: item.premium,
    coverage_summary: item.coverage_summary,
  }
}

export function DashboardPage() {
  const [items, setItems] = useState<InsuranceItem[]>([])
  const [category, setCategory] = useState<Category | ''>('')
  const [status, setStatus] = useState<Status | ''>('')
  const [selected, setSelected] = useState<InsuranceItem | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      setItems(await listItems({ category: category || undefined, status: status || undefined }))
      setError(null)
    } catch (listError) {
      setError(listError instanceof Error ? listError.message : 'Could not load policies')
    } finally {
      setLoading(false)
    }
  }, [category, status])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const handleSave = async (values: ItemFormValues) => {
    if (!selected) return
    await updateItem(selected.id, values)
    setSelected(null)
    await refresh()
  }

  const handleDelete = async () => {
    if (!selected) return
    await deleteItem(selected.id)
    setSelected(null)
    await refresh()
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Your policies</h1>
        <Link
          to="/upload"
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Add policy
        </Link>
      </div>

      <FilterBar category={category} status={status} onCategory={setCategory} onStatus={setStatus} />

      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading ? <p className="text-slate-500">Loading…</p> : <ItemsTable items={items} onSelect={setSelected} />}

      {selected && (
        <section className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-lg font-semibold">Edit “{selected.item_name}”</h2>
            <div className="flex gap-3">
              {selected.source_document_ref && (
                <button
                  onClick={() => void downloadDocument(selected)}
                  className="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
                >
                  Download document
                </button>
              )}
              <button
                onClick={handleDelete}
                className="rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          </div>
          <ReviewForm
            key={selected.id}
            initial={toFormValues(selected)}
            rawText={selected.raw_extracted_text}
            submitLabel="Save changes"
            onSubmit={handleSave}
            onCancel={() => setSelected(null)}
          />
        </section>
      )}
    </div>
  )
}
