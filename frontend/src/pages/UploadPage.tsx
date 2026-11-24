import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { createItem, extractDraft } from '../api/items'
import { ReviewForm, emptyFormValues } from '../components/ReviewForm'
import { UploadZone } from '../components/UploadZone'
import type { ExtractionDraft, ItemFormValues } from '../types'

function draftToFormValues(draft: ExtractionDraft): ItemFormValues {
  const blank = emptyFormValues()
  return {
    item_name: draft.item_name ?? blank.item_name,
    category: draft.category ?? blank.category,
    provider_name: draft.provider_name ?? blank.provider_name,
    provider_contact: draft.provider_contact,
    policy_number: draft.policy_number,
    coverage_start: draft.coverage_start ?? blank.coverage_start,
    coverage_end: draft.coverage_end,
    premium: draft.premium,
    coverage_summary: draft.coverage_summary,
  }
}

export function UploadPage() {
  const navigate = useNavigate()
  const [draft, setDraft] = useState<ExtractionDraft | null>(null)
  const [manual, setManual] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = async (file: File) => {
    setError(null)
    setExtracting(true)
    try {
      setDraft(await extractDraft(file))
    } catch (extractError) {
      setError(extractError instanceof Error ? extractError.message : 'Could not read this PDF')
    } finally {
      setExtracting(false)
    }
  }

  const handleSave = async (values: ItemFormValues) => {
    await createItem(
      values,
      draft
        ? {
            source_document_ref: draft.source_document_ref,
            raw_extracted_text: draft.raw_extracted_text,
            extraction_confidence: draft.extraction_confidence ?? undefined,
          }
        : {},
    )
    navigate('/')
  }

  if (draft || manual) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold">Review before saving</h1>
        <p className="text-slate-600">
          {draft
            ? 'Correct anything the extractor got wrong, then save.'
            : 'Enter the policy details manually.'}
        </p>
        <ReviewForm
          initial={draft ? draftToFormValues(draft) : emptyFormValues()}
          confidence={draft?.extraction_confidence}
          rawText={draft?.raw_extracted_text}
          submitLabel="Confirm & save"
          onSubmit={handleSave}
          onCancel={() => {
            setDraft(null)
            setManual(false)
          }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Add a policy</h1>
      <UploadZone onFile={handleFile} disabled={extracting} />
      {extracting && <p className="text-slate-600">Reading the PDF and extracting details…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button onClick={() => setManual(true)} className="text-sm text-blue-600 hover:underline">
        Skip upload — enter details manually
      </button>
    </div>
  )
}
