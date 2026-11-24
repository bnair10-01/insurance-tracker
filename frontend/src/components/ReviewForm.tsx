import { useState, type FormEvent } from 'react'

import { CATEGORIES, PREMIUM_FREQUENCIES, type Category, type ItemFormValues, type PremiumFrequency } from '../types'

interface Props {
  initial: ItemFormValues
  confidence?: number | null
  rawText?: string | null
  submitLabel: string
  onSubmit: (values: ItemFormValues) => Promise<void>
  onCancel?: () => void
}

export function emptyFormValues(): ItemFormValues {
  return {
    item_name: '',
    category: 'other',
    provider_name: '',
    provider_contact: { phone: null, email: null, website: null, agent_name: null },
    policy_number: null,
    coverage_start: new Date().toISOString().slice(0, 10),
    coverage_end: null,
    premium: { amount: null, frequency: null },
    coverage_summary: null,
  }
}

function ConfidenceBadge({ value }: { value: number }) {
  const className =
    value >= 0.8 ? 'bg-emerald-100 text-emerald-800' : value >= 0.5 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
  const label = value >= 0.8 ? 'High confidence' : value >= 0.5 ? 'Medium confidence' : 'Low confidence'
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`} title={`${(value * 100).toFixed(0)}%`}>
      {label} · {(value * 100).toFixed(0)}%
    </span>
  )
}

const inputClass = 'w-full rounded border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'
const labelClass = 'mb-1 block text-sm font-medium text-slate-700'

export function ReviewForm({ initial, confidence, rawText, submitLabel, onSubmit, onCancel }: Props) {
  const [values, setValues] = useState<ItemFormValues>(initial)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [showRaw, setShowRaw] = useState(false)

  const set = <K extends keyof ItemFormValues>(key: K, value: ItemFormValues[K]) =>
    setValues((current) => ({ ...current, [key]: value }))

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setSaving(true)
    try {
      await onSubmit(values)
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Could not save this policy')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-slate-200 bg-white p-6">
      {confidence != null && (
        <div className="flex items-center gap-3 rounded bg-slate-50 p-3">
          <ConfidenceBadge value={confidence} />
          <span className="text-sm text-slate-600">
            These fields were read from the PDF automatically. Check them before saving.
          </span>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={labelClass}>Item name</label>
          <input
            className={inputClass}
            required
            value={values.item_name}
            onChange={(e) => set('item_name', e.target.value)}
            placeholder="2021 Honda Civic"
          />
        </div>
        <div>
          <label className={labelClass}>Category</label>
          <select
            className={inputClass}
            value={values.category}
            onChange={(e) => set('category', e.target.value as Category)}
          >
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Provider</label>
          <input
            className={inputClass}
            required
            value={values.provider_name}
            onChange={(e) => set('provider_name', e.target.value)}
          />
        </div>
        <div>
          <label className={labelClass}>Policy number</label>
          <input
            className={inputClass}
            value={values.policy_number ?? ''}
            onChange={(e) => set('policy_number', e.target.value || null)}
          />
        </div>
        <div>
          <label className={labelClass}>Coverage start</label>
          <input
            type="date"
            className={inputClass}
            required
            value={values.coverage_start}
            onChange={(e) => set('coverage_start', e.target.value)}
          />
        </div>
        <div>
          <label className={labelClass}>Coverage end</label>
          <input
            type="date"
            className={inputClass}
            value={values.coverage_end ?? ''}
            onChange={(e) => set('coverage_end', e.target.value || null)}
          />
        </div>
        <div>
          <label className={labelClass}>Premium amount</label>
          <input
            type="number"
            step="0.01"
            min="0"
            className={inputClass}
            value={values.premium.amount ?? ''}
            onChange={(e) =>
              set('premium', { ...values.premium, amount: e.target.value === '' ? null : Number(e.target.value) })
            }
          />
        </div>
        <div>
          <label className={labelClass}>Premium frequency</label>
          <select
            className={inputClass}
            value={values.premium.frequency ?? ''}
            onChange={(e) =>
              set('premium', {
                ...values.premium,
                frequency: e.target.value === '' ? null : (e.target.value as PremiumFrequency),
              })
            }
          >
            <option value="">—</option>
            {PREMIUM_FREQUENCIES.map((frequency) => (
              <option key={frequency} value={frequency}>
                {frequency}
              </option>
            ))}
          </select>
        </div>
      </div>

      <fieldset className="grid gap-4 sm:grid-cols-2">
        <legend className="mb-2 text-sm font-semibold text-slate-800">Provider contact</legend>
        {(['phone', 'email', 'website', 'agent_name'] as const).map((field) => (
          <div key={field}>
            <label className={labelClass}>{field.replace('_', ' ')}</label>
            <input
              className={inputClass}
              value={values.provider_contact[field] ?? ''}
              onChange={(e) =>
                set('provider_contact', { ...values.provider_contact, [field]: e.target.value || null })
              }
            />
          </div>
        ))}
      </fieldset>

      <div>
        <label className={labelClass}>Coverage summary</label>
        <textarea
          className={inputClass}
          rows={3}
          value={values.coverage_summary ?? ''}
          onChange={(e) => set('coverage_summary', e.target.value || null)}
        />
      </div>

      {rawText && (
        <div>
          <button
            type="button"
            className="text-sm text-blue-600 hover:underline"
            onClick={() => setShowRaw((shown) => !shown)}
          >
            {showRaw ? 'Hide' : 'Show'} text read from the PDF
          </button>
          {showRaw && (
            <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap rounded bg-slate-100 p-3 text-xs text-slate-700">
              {rawText}
            </pre>
          )}
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? 'Saving…' : submitLabel}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
