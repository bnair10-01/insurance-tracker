import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

import * as authApi from '../api/auth'
import { clearToken, getToken, setToken } from '../api/client'

interface AuthValue {
  isAuthenticated: boolean
  signup: (email: string, password: string) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(getToken())

  const adopt = useCallback((accessToken: string) => {
    setToken(accessToken)
    setTokenState(accessToken)
  }, [])

  const value = useMemo<AuthValue>(
    () => ({
      isAuthenticated: token !== null,
      signup: async (email, password) => {
        const { access_token } = await authApi.signup(email, password)
        adopt(access_token)
      },
      login: async (email, password) => {
        const { access_token } = await authApi.login(email, password)
        adopt(access_token)
      },
      logout: () => {
        clearToken()
        setTokenState(null)
      },
    }),
    [token, adopt],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
