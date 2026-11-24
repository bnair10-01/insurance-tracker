import type { Category, ExtractionDraft, InsuranceItem, ItemFormValues, Status } from '../types'
import { getToken, request } from './client'

export function listItems(filters: { category?: Category; status?: Status } = {}): Promise<InsuranceItem[]> {
  const params = new URLSearchParams()
  if (filters.category) params.set('category', filters.category)
  if (filters.status) params.set('status', filters.status)
  const query = params.toString()
  return request<InsuranceItem[]>(`/api/items${query ? `?${query}` : ''}`)
}

export function getItem(id: string): Promise<InsuranceItem> {
  return request<InsuranceItem>(`/api/items/${id}`)
}

export function createItem(
  values: ItemFormValues,
  extras: Partial<Pick<ExtractionDraft, 'source_document_ref' | 'raw_extracted_text' | 'extraction_confidence'>> = {},
): Promise<InsuranceItem> {
  return request<InsuranceItem>('/api/items', {
    method: 'POST',
    body: JSON.stringify({ ...values, ...extras, source_channel: 'manual_upload' }),
  })
}

export function updateItem(id: string, values: ItemFormValues): Promise<InsuranceItem> {
  return request<InsuranceItem>(`/api/items/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(values),
  })
}

export function deleteItem(id: string): Promise<void> {
  return request<void>(`/api/items/${id}`, { method: 'DELETE' })
}

export function extractDraft(file: File): Promise<ExtractionDraft> {
  const body = new FormData()
  body.append('file', file)
  return request<ExtractionDraft>('/api/documents/extract', { method: 'POST', body })
}

export async function downloadDocument(item: InsuranceItem): Promise<void> {
  const response = await fetch(`/api/items/${item.id}/document`, {
    headers: { Authorization: `Bearer ${getToken() ?? ''}` },
  })
  if (!response.ok) throw new Error('Could not download the stored document')

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${item.item_name}.pdf`
  link.click()
  URL.revokeObjectURL(url)
}
