import { request } from './client'

interface TokenResponse {
  access_token: string
  token_type: string
}

export function signup(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function me(): Promise<{ id: string; email: string }> {
  return request('/api/auth/me')
}
