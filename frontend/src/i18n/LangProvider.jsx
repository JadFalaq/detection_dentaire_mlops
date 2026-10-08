import { useEffect, useMemo, useState } from 'react'
import { LangContext } from './context'
import ar from './ar'
import fr from './fr'

const DICTIONARIES = { fr, ar }
const STORAGE_KEY = 'snani-lang'

function initialLang() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && saved in DICTIONARIES) {
      return saved
    }
  } catch {
    // storage can be unavailable (private mode, blocked cookies)
  }
  return navigator.language?.toLowerCase().startsWith('ar') ? 'ar' : 'fr'
}

export function LangProvider({ children }) {
  const [lang, setLang] = useState(initialLang)
  const dir = lang === 'ar' ? 'rtl' : 'ltr'

  useEffect(() => {
    document.documentElement.lang = lang
    document.documentElement.dir = dir
    try {
      localStorage.setItem(STORAGE_KEY, lang)
    } catch {
      // ignore
    }
  }, [lang, dir])

  const value = useMemo(
    () => ({
      lang,
      dir,
      t: DICTIONARIES[lang],
      toggleLang: () => setLang((current) => (current === 'fr' ? 'ar' : 'fr')),
    }),
    [lang, dir],
  )

  return <LangContext.Provider value={value}>{children}</LangContext.Provider>
}
