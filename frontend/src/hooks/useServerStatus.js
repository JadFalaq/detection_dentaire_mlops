import { useCallback, useEffect, useRef, useState } from 'react'
import { MOCK_API, apiFetch } from '../api'

const POLL_INTERVAL_MS = 3000
const GIVE_UP_AFTER_MS = 150000
// Azure Container Apps scales the replica back to zero ~300 s after the last request.
const SLEEP_AFTER_MS = 280000

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// The backend scales to zero and is billed only while awake. Nothing here runs on page
// load: the server is contacted only when a visitor actually starts a test (`wake`).
export function useServerStatus() {
  const [status, setStatus] = useState(MOCK_API ? 'demo' : 'sleeping')
  const [wakeRequest, setWakeRequest] = useState(0)
  const sleepTimerRef = useRef(null)
  const statusRef = useRef(status)

  useEffect(() => {
    statusRef.current = status
  }, [status])

  const markActive = useCallback(() => {
    if (MOCK_API) return
    clearTimeout(sleepTimerRef.current)
    sleepTimerRef.current = setTimeout(() => setStatus('sleeping'), SLEEP_AFTER_MS)
  }, [])

  useEffect(() => {
    if (MOCK_API || wakeRequest === 0) {
      return undefined
    }
    let cancelled = false
    const startedAt = Date.now()

    async function poll() {
      while (!cancelled) {
        try {
          const response = await apiFetch('/health', { signal: AbortSignal.timeout(30000) })
          if (response.ok) {
            if (!cancelled) {
              setStatus('ready')
              markActive()
            }
            return
          }
        } catch {
          // still waking up or unreachable
        }
        if (cancelled) return
        if (Date.now() - startedAt > GIVE_UP_AFTER_MS) {
          setStatus('offline')
          return
        }
        setStatus('waking')
        await wait(POLL_INTERVAL_MS)
      }
    }

    poll()
    return () => {
      cancelled = true
    }
  }, [wakeRequest, markActive])

  useEffect(() => () => clearTimeout(sleepTimerRef.current), [])

  const wake = useCallback(() => {
    if (MOCK_API) return
    if (statusRef.current === 'ready') {
      markActive()
      return
    }
    if (statusRef.current === 'checking' || statusRef.current === 'waking') return
    setStatus('checking')
    setWakeRequest((value) => value + 1)
  }, [markActive])

  return { status, wake, markActive }
}
