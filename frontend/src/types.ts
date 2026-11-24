export const CATEGORIES = [
  'auto',
  'home',
  'health',
  'life',
  'gadget',
  'travel',
  'pet',
  'other',
] as const

export const STATUSES = ['active', 'upcoming', 'expiring_soon', 'expired', 'unknown'] as const

export const PREMIUM_FREQUENCIES = ['monthly', 'annual', 'one-time'] as const

export type Category = (typeof CATEGORIES)[number]
export type Status = (typeof STATUSES)[number]
export type PremiumFrequency = (typeof PREMIUM_FREQUENCIES)[number]

export interface ProviderContact {
  phone: string | null
  email: string | null
  website: string | null
  agent_name: string | null
}

export interface Premium {
  amount: number | null
  frequency: PremiumFrequency | null
}

export interface InsuranceItem {
  id: string
  user_id: string
  item_name: string
  category: Category
  provider_name: string
  provider_contact: ProviderContact
  policy_number: string | null
  coverage_start: string
  coverage_end: string | null
  premium: Premium
  coverage_summary: string | null
  status: Status
  source_channel: 'email' | 'manual_upload' | 'telegram_upload'
  source_document_ref: string | null
  extraction_confidence: number | null
  date_added: string
  last_verified: string | null
  raw_extracted_text: string | null
}

export interface ExtractionDraft {
  item_name: string | null
  category: Category | null
  provider_name: string | null
  provider_contact: ProviderContact
  policy_number: string | null
  coverage_start: string | null
  coverage_end: string | null
  premium: Premium
  coverage_summary: string | null
  extraction_confidence: number | null
  source_document_ref: string
  raw_extracted_text: string
}

export interface ItemFormValues {
  item_name: string
  category: Category
  provider_name: string
  provider_contact: ProviderContact
  policy_number: string | null
  coverage_start: string
  coverage_end: string | null
  premium: Premium
  coverage_summary: string | null
}
