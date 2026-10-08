import { createContext, useContext } from 'react'

export const LangContext = createContext(null)

export function useI18n() {
  return useContext(LangContext)
}
